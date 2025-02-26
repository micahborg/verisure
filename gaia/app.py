# app.py - Main application file
import os
import json
import requests
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import uvicorn
from claim_extractor import ClaimExtractor, process_claim_file
from claim_validator import ClaimValidator
from zk_proof_generator import generate_zk_proof
# from othentic_client import send_proof_to_aggregators

# Initialize FastAPI app
app = FastAPI(title="Insurance Claim Processor", 
              description="AI-powered insurance claim processing system")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Constants
GAIA_NODE_URL = "https://0x8600b7fb770322a38c1ba3e8fcab1f73c6cc701b.gaia.domains/v1"
TEMP_FILE_DIR = "temp_files"

# Ensure temp directory exists
os.makedirs(TEMP_FILE_DIR, exist_ok=True)

# Response models
class ClaimResponse(BaseModel):
    claim_data: Dict[str, Any]
    validation_results: Dict[str, Any]
    zk_proof: Optional[Dict[str, Any]] = None
    aggregator_response: Optional[Dict[str, Any]] = None
    ai_analysis: Optional[str] = None

@app.post("/process-claim/", response_model=ClaimResponse)
async def process_claim(
    pdf_file: UploadFile = File(...),
    generate_proof: bool = Form(False),
    send_to_aggregators: bool = Form(False)
):
    """
    Process an insurance claim PDF file, validate data, and optionally generate and send ZK proofs
    """
    # Save uploaded file
    temp_pdf_path = os.path.join(TEMP_FILE_DIR, pdf_file.filename)
    with open(temp_pdf_path, "wb") as buffer:
        buffer.write(await pdf_file.read())
    
    try:
        # 1. Extract data from PDF
        claim_data = process_claim_file(temp_pdf_path)
        
        # 2. Validate claim data
        validator = ClaimValidator(claim_data)
        validation_results = validator.validate_all()
        
        # Create response object
        response = {
            "claim_data": claim_data,
            "validation_results": validation_results
        }
        
        # 3. Process with AI (using GaiaNet node)
        ai_analysis = await analyze_with_gaia_ai(claim_data)
        response["ai_analysis"] = ai_analysis
        
        # 4. Generate zero-knowledge proof if requested
        if generate_proof:
            proof = generate_zk_proof(claim_data, validation_results)
            response["zk_proof"] = proof
            
            # 5. Send to aggregators if requested
            # if send_to_aggregators and proof:
            #     aggregator_response = send_proof_to_aggregators(proof)
            #     response["aggregator_response"] = aggregator_response
        
        return JSONResponse(content=response)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing claim: {str(e)}")
    finally:
        # Clean up temp file
        if os.path.exists(temp_pdf_path):
            os.remove(temp_pdf_path)

async def analyze_with_gaia_ai(claim_data: dict) -> str:
    """
    Sends claim data to the GaiaNet node for AI analysis
    """
    # Format claim data as a readable string
    claim_text = json.dumps(claim_data, indent=2)
    
    # Prepare prompt for the LLM
    messages = [
        {
            "role": "system", 
            "content": "You are an AI assistant specializing in health insurance claims processing. Analyze the given claim data and provide insights on eligibility, potential issues, and recommendations."
        },
        {
            "role": "user", 
            "content": f"Please analyze this health insurance claim data and provide your assessment:\n\n{claim_text}"
        }
    ]
    
    # Send request to GaiaNet node
    try:
        response = requests.post(
            f"{GAIA_NODE_URL}/chat/completions",
            json={
                "messages": messages,
                "temperature": 0.2,
                "max_tokens": 500
            },
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            return result["choices"][0]["message"]["content"]
        else:
            return f"Error analyzing claim with AI: {response.status_code} - {response.text}"
    
    except Exception as e:
        return f"Failed to connect to GaiaNet node: {str(e)}"

@app.get("/health")
async def health_check():
    """Simple health check endpoint"""
    return {"status": "healthy", "node_id": "0x8600b7fb770322a38c1ba3e8fcab1f73c6cc701b"}

# Test route to verify GaiaNet node connection
@app.get("/test-gaia-connection")
async def test_gaia_connection():
    """Test the connection to the GaiaNet node"""
    try:
        response = requests.post(
            f"{GAIA_NODE_URL}/chat/completions",
            json={
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": "Test connection. Reply with 'Connection successful!'"}
                ]
            },
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            return {
                "status": "success",
                "node_id": "0x8600b7fb770322a38c1ba3e8fcab1f73c6cc701b",
                "response": result["choices"][0]["message"]["content"]
            }
        else:
            return {
                "status": "error",
                "details": f"Status code: {response.status_code}, Response: {response.text}"
            }
    
    except Exception as e:
        return {"status": "error", "details": str(e)}

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)