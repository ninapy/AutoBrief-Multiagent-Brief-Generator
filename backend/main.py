from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware

import logging
from dotenv import load_dotenv
import os
from fastapi.responses import FileResponse

from agents.parser_agent import parse_file
from agents.briefer_agent import generate_brief
from utils.pdf_generator import generate_pdf

from agents.meeting_scheduler_agent import MeetingSchedulerAgent, TeamMember, meetings_to_dict
from mock_team_data import INFOSYS_TEAM, get_team_data_json
from typing import List, Optional

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
        MAX_FILE_SIZE = 15 * 1024 * 1024  # 10MB
        
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
    
# Initialize the meeting scheduler
meeting_scheduler = MeetingSchedulerAgent()

@app.post("/brief-with-meetings")
async def create_brief_with_meetings(
    file: UploadFile = File(...), 
    custom_team: Optional[List[dict]] = None
):
    """
    Enhanced endpoint that generates both brief and meeting schedule
    """
    try:
        # Step 1: Process the file and generate brief (your existing logic)
        content = await parse_file(file)
        if not content["success"]:
            raise HTTPException(400, content["error"])
        
        brief = generate_brief(content["content"])
        pdf_path = generate_pdf(brief)
        
        # Step 2: Use team data (custom or default)
        if custom_team:
            # Convert custom team data to TeamMember objects
            team_members = [
                TeamMember(
                    name=member["name"],
                    email=member["email"], 
                    role=member["role"],
                    department=member.get("department", "Unknown"),
                    specialties=member.get("specialties", [])
                )
                for member in custom_team
            ]
        else:
            # Use default EdgeVerve team
            team_members = INFOSYS_TEAM
        
        # Step 3: Generate meeting schedule
        meetings = meeting_scheduler.schedule_meetings_fast(brief, team_members)
        
        # Step 4: Return comprehensive response
        return {
            "success": True,
            "brief": brief,
            "pdf_path": pdf_path,
            "meetings": meetings_to_dict(meetings),
            "team_used": len(team_members),
            "file_info": {
                "filename": file.filename,
                "type": content["file_type"]
            }
        }
        
    except Exception as e:
        logger.error(f"Error in brief_with_meetings: {e}")
        raise HTTPException(500, f"Failed to process: {str(e)}")

@app.get("/download-pdf/{filename}")
async def download_pdf(filename: str):
    """
    Download the generated PDF file
    """
    try:
        # Security check - only allow specific filename
        if filename != "brief_output.pdf":
            raise HTTPException(404, "File not found")
        
        # Check if file exists
        if not os.path.exists(filename):
            raise HTTPException(404, "PDF file not found")
        
        return FileResponse(
            path=filename,
            filename=filename,
            media_type="application/pdf"
        )
        
    except Exception as e:
        logger.error(f"Error downloading PDF: {e}")
        raise HTTPException(500, "Failed to download PDF")

@app.get("/team-roster")
async def get_team_roster():
    """
    Get the default company team roster for frontend display
    """
    return {
        "success": True,
        "team": get_team_data_json(),
        "total_members": len(INFOSYS_TEAM)
    }

@app.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    return {"status": "healthy", "service": "creative-brief-generator"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)