from fastapi import FastAPI, File, UploadFile
from agents.parser_agent import parse_file
from agents.briefer_agent import generate_brief
from utils.pdf_generator import generate_pdf

app = FastAPI()

@app.post("/brief")
async def create_brief(file: UploadFile = File(...)):
    content = await parse_file(file)
    brief = generate_brief(content)
    pdf_path = generate_pdf(brief)
    return {"brief": brief, "pdf_path": pdf_path}
