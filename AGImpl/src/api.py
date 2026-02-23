import os
import shutil
import boto3
import mysql.connector
from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from .models import Briefcase
from .graph import create_graph
from dotenv import load_dotenv
# Load .env from the same directory as this file
env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
load_dotenv(dotenv_path=env_path)

app = FastAPI()

def setup_db():
    """Verify DB connection, create schema and seed data if necessary."""
    print("--- Initializing Database ---", flush=True)
    try:
        db_host = os.getenv("DB_HOST", "localhost")
        db_port = int(os.getenv("DB_PORT", "3306"))
        db_user = os.getenv("DB_USER", "admin")  # Default for RDS
        db_password = os.getenv("DB_PASSWORD")
        db_name = os.getenv("DB_NAME", "loyalty_db")
        
        if not db_password:
            print("WARNING: DB_PASSWORD not set. Skipping DB initialization.")
            return

        conn = mysql.connector.connect(
            host=db_host,
            port=db_port,
            user=db_user,
            password=db_password,
            database=db_name
        )
        cursor = conn.cursor()

        # 1. Create Users Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                ssn_last4 VARCHAR(4) NOT NULL,
                loyalty_tier VARCHAR(50),
                service_history TEXT
            )
        """)

        # 2. Create Applications Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS applications (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT,
                income DECIMAL(15, 2),
                apr DECIMAL(5, 4),
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)

        # 3. Seed "John Doe" if empty
        cursor.execute("SELECT COUNT(*) FROM users")
        count = cursor.fetchone()[0]
        if count == 0:
            print("Seeding John Doe test data...", flush=True)
            cursor.execute("""
                INSERT INTO users (name, ssn_last4, loyalty_tier, service_history)
                VALUES ('John Doe', '1234', 'Platinum', '6 visits')
            """)
            conn.commit()
            print("Seed complete.", flush=True)
        else:
            print(f"Database already contains {count} users.", flush=True)

        cursor.close()
        conn.close()
        print("--- Database Initialization Complete ---", flush=True)
    except Exception as e:
        print(f"CRITICAL ERROR in setup_db: {str(e)}", flush=True)

@app.on_event("startup")
async def startup_event():
    setup_db()

# S3 Configuration (AWS or LocalStack)
S3_BUCKET = os.getenv("S3_BUCKET", "loyalty-bucket")
USE_AWS = os.getenv("USE_AWS", "false").lower() == "true"

if USE_AWS:
    s3_client = boto3.client("s3", region_name=os.getenv("AWS_DEFAULT_REGION", "us-east-1"))
else:
    S3_ENDPOINT = "http://localhost:4566"
    s3_client = boto3.client(
        "s3",
        endpoint_url=S3_ENDPOINT,
        aws_access_key_id="test",
        aws_secret_access_key="test",
        region_name="us-east-1"
    )

class ProcessRequest(BaseModel):
    s3_path: str
    name: str
    ssn_last4: str

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        file_path = f"temp_{file.filename}"
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        s3_key = f"applications/{file.filename}"
        s3_client.upload_file(file_path, S3_BUCKET, s3_key)
        os.remove(file_path)
        
        return {"s3_path": f"s3://{S3_BUCKET}/{s3_key}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/process")
async def process_application(request: ProcessRequest):
    try:
        langgraph_app = create_graph()
        initial_state = Briefcase(
            s3_path=request.s3_path,
            name=request.name,
            ssn_last4=request.ssn_last4
        )
        
        final_state = langgraph_app.invoke(initial_state)
        print(f"Workflow Complete. Final State: {final_state}", flush=True)
        # Explicitly return as dict to avoid serialization issues
        output = final_state.dict() if hasattr(final_state, "dict") else final_state
        return output
    except Exception as e:
        import traceback
        print(f"CRITICAL ERROR in /process: {str(e)}", flush=True)
        print(traceback.format_exc(), flush=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/apply")
async def apply_loan(request: Briefcase):
    # In a real app, this would save the application to the SQL database
    return {"status": "success", "message": f"Loan locked in at {request.final_apr}% APR!"}

@app.get("/db-status")
async def db_status():
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
        
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM applications")
        app_count = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        return {
            "status": "connected",
            "database": db_name,
            "user_count": user_count,
            "application_count": app_count
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
