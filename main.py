from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from datetime import datetime
import os
import json
import secrets

app = FastAPI()
security = HTTPBasic()

# Hard-coded credentials for demonstration
VALID_USERNAME = "itsolutions"
VALID_PASSWORD = "hello"

# Ensure log directory exists
LOG_DIR = "request_logs"
os.makedirs(LOG_DIR, exist_ok=True)

def verify_credentials(credentials: HTTPBasicCredentials = Depends(security)):
    """Verify if the provided credentials are valid."""
    correct_username = secrets.compare_digest(credentials.username, VALID_USERNAME)
    correct_password = secrets.compare_digest(credentials.password, VALID_PASSWORD)
    
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

@app.get("/")
@app.post("/")
async def root(request: Request, username: str = Depends(verify_credentials)):
    """Handle both GET and POST requests at the root URL, validate credentials and log the request."""
    try:
        # Get request method
        method = request.method
        
        # Get client IP
        client_host = request.client.host
        
        # Try to get request body for POST requests
        body = None
        if method == "POST":
            try:
                body = await request.json()
            except:
                body = {"error": "Could not parse JSON body"}
        
        # Create log entry
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "method": method,
            "client_ip": client_host,
            "username": username,
            "headers": dict(request.headers)
        }
        
        # Add body for POST requests
        if body:
            log_entry["request_body"] = body
        
        # Add query params for GET requests
        if method == "GET":
            log_entry["query_params"] = dict(request.query_params)
        
        # Create a unique filename based on timestamp
        filename = f"{LOG_DIR}/request_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}.json"
        
        # Write log to file
        with open(filename, "w") as f:
            json.dump(log_entry, f, indent=2)
        
        return {
            "status": "success",
            "message": f"Request logged successfully to {os.path.basename(filename)}",
            "method": method,
            "authenticated_user": username
        }
        
    except Exception as e:
        # Log the error
        error_log = {
            "timestamp": datetime.now().isoformat(),
            "error": str(e),
            "method": request.method,
            "path": request.url.path
        }
        
        error_filename = f"{LOG_DIR}/error_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}.json"
        with open(error_filename, "w") as f:
            json.dump(error_log, f, indent=2)
        
        # If it's not already an HTTPException, wrap it
        if not isinstance(e, HTTPException):
            raise HTTPException(
                status_code=500,
                detail=f"Internal server error: {str(e)}"
            )
        raise

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)