from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from agents.parser_agent import parse_file
import logging
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Creative Brief Generator API", version="1.0.0")

# Add CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Creative Brief Generator API is running!"}

@app.post("/parse")
async def parse_uploaded_file(file: UploadFile = File(...)):
    """
    Parse uploaded file and extract text content
    """
    try:
        # Validate file size (optional - adjust as needed)
        MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
        
        # Check if file is too large
        file_size = 0
        file_content = await file.read()
        file_size = len(file_content)
        
        if file_size > MAX_FILE_SIZE:
            raise HTTPException(status_code=413, detail="File too large")
        
        # Reset file pointer for processing
        await file.seek(0)
        
        # Parse the file
        result = await parse_file(file)
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return {
            "success": True,
            "filename": result["filename"],
            "file_type": result["file_type"],
            "content": result["content"],
            "content_length": len(result["content"])
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in parse endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/brief")
async def create_brief(file: UploadFile = File(...)):
    """
    Full pipeline: Parse file and generate brief
    This will be completed when your teammate finishes the briefer agent
    """
    try:
        # Step 1: Parse the file
        parse_result = await parse_file(file)
        
        if not parse_result["success"]:
            raise HTTPException(status_code=400, detail=parse_result["error"])
        
        # Step 2: Generate brief (placeholder for now)
        # brief_result = generate_brief(parse_result["content"])
        
        return {
            "success": True,
            "parsed_content": parse_result["content"],
            "brief": "Brief generation will be implemented by teammate",
            "message": "File parsed successfully, brief generation pending"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in brief endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    return {"status": "healthy", "service": "creative-brief-generator"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)