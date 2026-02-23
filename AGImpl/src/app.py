import streamlit as st
import requests
import os

# Configuration
API_URL = "http://localhost:8001"

st.set_page_config(page_title="AutoFin Loyalty Program", layout="centered")

st.title("🚗 AutoFin Loan Application")
st.subheader("Loyalty Reward Program")

# Initialize session state for multi-stage flow
if "stage" not in st.session_state:
    st.session_state.stage = "identity"

# --- Stage 1: Identity ---
if st.session_state.stage == "identity":
    st.header("Step 1: Who are you?")
    name = st.text_input("Full Name", value="John Doe")
    ssn = st.text_input("Last 4 digits of SSN", type="password", max_chars=4)
    
    if st.button("Next"):
        if name and len(ssn) == 4:
            st.session_state.name = name
            st.session_state.ssn = ssn
            st.session_state.stage = "consent"
            st.rerun()
        else:
            st.error("Please enter a valid Name and 4-digit SSN.")

# --- Stage 2: Consent ---
elif st.session_state.stage == "consent":
    st.header("Step 2: AI Consent")
    st.write(f"Hello, {st.session_state.name}.")
    consent = st.checkbox("I consent to AI-powered processing of my income documents.")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Back"):
            st.session_state.stage = "identity"
            st.rerun()
    with col2:
        if st.button("Agree & Continue"):
            if consent:
                st.session_state.stage = "upload"
                st.rerun()
            else:
                st.warning("You must provide consent to proceed.")

# --- Stage 3: Upload ---
elif st.session_state.stage == "upload":
    st.header("Step 3: Income Verification")
    st.info("Upload your latest paystub or tax document (Image/PDF).")
    uploaded_file = st.file_uploader("Drop your paystub here", type=['png', 'jpg', 'jpeg', 'pdf'])
    
    if uploaded_file and st.button("Process with AI"):
        with st.spinner("Processing documents..."):
            # 1. Upload to S3 via FastAPI
            files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
            upload_response = requests.post(f"{API_URL}/upload", files=files)
            
            if upload_response.status_code == 200:
                s3_path = upload_response.json().get("s3_path")
                
                # 2. Trigger LangGraph Workflow
                payload = {
                    "s3_path": s3_path, 
                    "name": st.session_state.name,
                    "ssn_last4": st.session_state.ssn
                }
                process_response = requests.post(f"{API_URL}/process", json=payload)
                
                if process_response.status_code == 200:
                    result = process_response.json()
                    if result.get("error"):
                        st.error(result.get("error"))
                    else:
                        st.session_state.result = result
                        st.session_state.stage = "reward"
                        st.rerun()
                else:
                    st.error("Error processing document with AI.")
            else:
                st.error("S3 Upload failed.")

# --- Stage 4: Interaction ---
elif st.session_state.stage == "reward":
    st.balloons()
    res = st.session_state.result
    
    st.success("Analysis Complete!")
    
    # Loyalty Reward Card
    with st.container(border=True):
        st.markdown(f"### 🏆 Loyalty Reward: {res.get('loyalty_tier', 'Standard')}")
        st.write(f"**Verified Name:** {res.get('name')}")
        st.write(f"**Extracted Income:** ${res.get('income'):,.2f}")
        
        st.divider()
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Base APR", f"{res.get('base_apr')}%")
        with col2:
            st.metric("Your Discounted APR", f"{res.get('final_apr')}%", delta=f"-{res.get('base_apr') - res.get('final_apr')}%", delta_color="inverse")
        
        if st.button("🚀 Lock In This APR", use_container_width=True):
            apply_response = requests.post(f"{API_URL}/apply", json=res)
            if apply_response.status_code == 200:
                st.session_state.stage = "success"
                st.rerun()

elif st.session_state.stage == "success":
    st.header("🎉 Application Success!")
    st.write(f"Thank you, {st.session_state.name}. Your loan application has been submitted with your loyalty discount.")
    if st.button("Start New Application"):
        st.session_state.stage = "identity"
        st.rerun()
