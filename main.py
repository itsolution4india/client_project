from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from datetime import datetime
import os
import json

app = FastAPI()
security = HTTPBasic()

# Hard-coded credentials for demonstration
# In a real application, you would use a more secure method
VALID_USERNAME = "itsolutions"
VALID_PASSWORD = "testing"

# Ensure log directory exists
LOG_DIR = "request_logs"
os.makedirs(LOG_DIR, exist_ok=True)

def verify_credentials(credentials: HTTPBasicCredentials = Depends(security)):
    """Verify if the provided credentials are valid."""
    if credentials.username == VALID_USERNAME and credentials.password == VALID_PASSWORD:
        return True
    raise HTTPException(
        status_code=401,
        detail="Invalid credentials",
        headers={"WWW-Authenticate": "Basic"},
    )

@app.post("/log")
async def log_request(request: Request, authenticated: bool = Depends(verify_credentials)):
    """Log the incoming request if credentials are valid."""
    # Get request body
    body = await request.json()
    
    # Get client IP
    client_host = request.client.host
    
    # Create log entry
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "client_ip": client_host,
        "request_body": body,
        "headers": dict(request.headers)
    }
    
    # Create a unique filename based on timestamp
    filename = f"{LOG_DIR}/request_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}.json"
    
    # Write log to file
    with open(filename, "w") as f:
        json.dump(log_entry, f, indent=2)
    
    return {"status": "success", "message": "Request logged successfully"}

@app.get("/")
async def root(authenticated: bool = Depends(verify_credentials)):
    """Simple endpoint to verify the API is working."""
    return {"message": "API is running. Send POST requests to /log endpoint."}

if __name__ == "__main__":
    import uvicorn
    # Make sure to bind to 0.0.0.0 to accept external connections
    uvicorn.run(app, host="0.0.0.0", port=8000)