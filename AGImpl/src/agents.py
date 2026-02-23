import os
import mysql.connector
from typing import Dict, Any
from .models import Briefcase
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
import boto3
import sys
from dotenv import load_dotenv
# Load .env from the same directory as this file
env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
load_dotenv(dotenv_path=env_path)

def node_screener(state: Briefcase) -> Dict[str, Any]:
    """Agent A (Screener): Extract Income/Name via LLM from S3 image path."""
    print(f"--- Executing Screener Node for {state.s3_path} ---", flush=True)
    
    try:
        # Initialize Gemini
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print(f"DEBUG: Current Environment Keys: {list(os.environ.keys())}", flush=True)
            print("ERROR: GEMINI_API_KEY is not set in environment.", flush=True)
            raise ValueError("GEMINI_API_KEY not found")
            
        print(f"DEBUG: GEMINI_API_KEY found (length: {len(api_key)})", flush=True)
        llm = ChatGoogleGenerativeAI(model="gemini-flash-latest", google_api_key=api_key)
        
        # 1. Parse S3 Path
        path_parts = state.s3_path.replace("s3://", "").split("/", 1)
        bucket = path_parts[0]
        key = path_parts[1]
        
        # 2. Get file from S3 (AWS or LocalStack)
        use_aws = os.getenv("USE_AWS", "false").lower() == "true"
        if use_aws:
            print("Connecting to AWS S3...", flush=True)
            s3 = boto3.client("s3", region_name=os.getenv("AWS_DEFAULT_REGION", "us-east-1"))
        else:
            s3_endpoint = "http://localhost:4566"
            print(f"Connecting to LocalStack S3 at {s3_endpoint}...", flush=True)
            s3 = boto3.client(
                "s3", 
                endpoint_url=s3_endpoint,
                aws_access_key_id="test",
                aws_secret_access_key="test",
                region_name="us-east-1"
            )
        
        print(f"Downloading from S3: {bucket}/{key}", flush=True)
        response = s3.get_object(Bucket=bucket, Key=key)
        image_data = response['Body'].read()
        print(f"Downloaded {len(image_data)} bytes.", flush=True)
        
        # 3. Create HumanMessage with image for Gemini
        import base64
        b64_image = base64.b64encode(image_data).decode("utf-8")
        
        message = HumanMessage(
            content=[
                {"type": "text", "text": "Analyze this document and extract the following fields. Respond ONLY in JSON format. \nFields: \n1. 'name': Full Name of the employee. \n2. 'income': Total Annual Income (number only). \n3. 'ssn': Last 4 digits of the Social Security Number. \n\nExample Output: {\"name\": \"John Doe\", \"income\": 75000.0, \"ssn\": \"1234\"}"},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64_image}"}}
            ]
        )
        
        print("Calling Gemini API...", flush=True)
        result = llm.invoke([message])
        
        print(f"DEBUG: Gemini raw content type: {type(result.content)}", flush=True)
        content_str = result.content
        if isinstance(content_str, list):
            # If it's a list, join the text parts
            text_parts = []
            for part in content_str:
                if isinstance(part, dict) and 'text' in part:
                    text_parts.append(part['text'])
                elif isinstance(part, str):
                    text_parts.append(part)
            content_str = "".join(text_parts)
        
        import json
        clean_content = content_str.strip().replace("```json", "").replace("```", "")
        data = json.loads(clean_content)
        print(f"SUCCESS: Gemini Extracted: {data}", flush=True)
        
        extracted_name = data.get("name", "Unknown")
        extracted_income = float(data.get("income", 0.0))
        extracted_ssn = str(data.get("ssn", ""))
        
        # Validation Logic
        error = None
        if extracted_ssn != state.ssn_last4:
            print(f"VALIDATION FAILED: Extracted SSN {extracted_ssn} != Provided {state.ssn_last4}", flush=True)
            error = "Can not proceed! , upload again income doc.."
            
        return {
            "name": extracted_name,
            "income": extracted_income,
            "extracted_ssn": extracted_ssn,
            "error": error
        }
    except Exception as e:
        import traceback
        error_msg = f"ERROR in Screener Node: {str(e)}"
        print(error_msg, flush=True)
        print(traceback.format_exc(), flush=True)
        # Return the error message to the UI to trigger the "Can not proceed" logic
        return {
            "name": "Screener Error Fallback", 
            "income": 0.0, 
            "error": "Can not proceed! , upload again income doc.."
        }

def node_miner(state: Briefcase) -> Dict[str, Any]:
    """Agent B (Miner): Search MySQL for Name match -> Retrieve Loyalty Tier."""
    if state.error:
        print(f"--- Skipping Miner Node due to error: {state.error} ---")
        return {}
    print("--- Executing Miner Node ---")
    
    tier = "Standard"
    try:
        db_host = os.getenv("DB_HOST", "localhost")
        db_port = int(os.getenv("DB_PORT", "3306"))
        db_user = os.getenv("DB_USER", "admin")
        db_password = os.getenv("DB_PASSWORD")
        db_name = os.getenv("DB_NAME", "loyalty_db")
        conn = mysql.connector.connect(
            host=db_host,
            port=db_port,
            user=db_user,
            password=db_password,
            database=db_name
        )
        cursor = conn.cursor()
        query = "SELECT loyalty_tier FROM users WHERE name = %s"
        cursor.execute(query, (state.name,))
        result = cursor.fetchone()
        if result:
            tier = result[0]
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error connecting to MySQL: {e}")
        # Default to Standard if DB fails
        
    return {"loyalty_tier": tier}

def node_calculator(state: Briefcase) -> Dict[str, Any]:
    """Service C (Calculator): Adjust APR (Base 6% - Loyalty Discount)."""
    if state.error:
        print(f"--- Skipping Calculator Node due to error: {state.error} ---")
        return {}
    print("--- Executing Calculator Node ---")
    
    discount = 0.0
    if state.loyalty_tier == "Platinum":
        discount = 2.0
    elif state.loyalty_tier == "Gold":
        discount = 1.0
    elif state.loyalty_tier == "Silver":
        discount = 0.5
        
    final_apr = state.base_apr - discount
    return {"final_apr": final_apr}
