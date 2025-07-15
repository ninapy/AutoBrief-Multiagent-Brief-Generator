from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware

import logging
from dotenv import load_dotenv
import os
from fastapi.responses import FileResponse

from backend.agents.parser_agent import parse_file
from backend.agents.briefer_agent import generate_brief
from backend.utils.pdf_generator import generate_pdf


load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Creative Brief Generator API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
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
        MAX_FILE_SIZE = 10 * 1024 * 1024
        
        file_size = 0
        file_content = await file.read()
        file_size = len(file_content)
        
        if file_size > MAX_FILE_SIZE:
            raise HTTPException(status_code=413, detail="File too large")
        
        await file.seek(0)
        
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
    try:
        parse_result = await parse_file(file)
        if not parse_result["success"]:
            raise HTTPException(status_code=400, detail=parse_result["error"])

        brief_result = generate_brief(parse_result["content"])
        pdf_path = generate_pdf(brief_result, "brief_output.pdf")

        return FileResponse(
            path=pdf_path,
            filename="brief_output.pdf",
            media_type="application/pdf"
        )
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