import filetype
from utils.file_loader import load_pdf, load_image, load_text, transcribe_audio

async def parse_file(uploaded_file):
    file_bytes = await uploaded_file.read()
    kind = filetype.guess(file_bytes)
    
    if uploaded_file.filename.endswith(".pdf"):
        return load_pdf(file_bytes)
    elif uploaded_file.filename.endswith(".jpg") or uploaded_file.filename.endswith(".png"):
        return load_image(file_bytes)
    elif uploaded_file.filename.endswith(".txt"):
        return load_text(file_bytes)
    elif uploaded_file.filename.endswith(".mp4"):
        return transcribe_audio(file_bytes)
    else:
        return "Unsupported file format"
