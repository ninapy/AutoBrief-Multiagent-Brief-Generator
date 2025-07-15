import filetype
import logging
from utils.file_loader import load_audio, load_pdf, load_image, load_text, load_csv, load_excel, load_video, normalize_text


# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def parse_file(uploaded_file):
    """
    Main parser agent that routes different file types to appropriate loaders
    """
    try:
        # Read file bytes
        file_bytes = await uploaded_file.read()
        filename = uploaded_file.filename.lower()
        
        logger.info(f"Processing file: {filename}")
        
        # Detect file type and route to appropriate loader
        if filename.endswith('.pdf'):
            logger.info("Detected PDF file")
            raw_text = load_pdf(file_bytes)
            
        elif filename.endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff')):
            logger.info("Detected image file")
            raw_text = load_image(file_bytes)
            
        elif filename.endswith(('.txt', '.md', '.rtf')):
            logger.info("Detected text file")
            raw_text = load_text(file_bytes)
        
        elif filename.endswith('.csv'):
            logger.info("Detected CSV file")
            raw_text = load_csv(file_bytes)
            
        elif filename.endswith(('.xlsx', '.xls')):
            logger.info("Detected Excel file")
            raw_text = load_excel(file_bytes)

        elif filename.endswith(('.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv', '.wmv')):
            logger.info("Detected video file")
            raw_text = load_video(file_bytes)

        elif filename.endswith(('.m4a', '.mp3', '.wav', '.aac', '.flac', '.ogg')):
            logger.info("Detected audio file")
            raw_text = load_audio(file_bytes)
            
        else:
            # Fall back to filetype detection if extension doesn't match
            kind = filetype.guess(file_bytes)
            
            if kind is None:
                return {
                    "success": False,
                    "error": "Unknown file type",
                    "content": None
                }
            
            if kind.mime.startswith('image/'):
                logger.info(f"Detected image file by MIME type: {kind.mime}")
                raw_text = load_image(file_bytes)
            elif kind.mime == 'application/pdf':
                logger.info("Detected PDF file by MIME type")
                raw_text = load_pdf(file_bytes)
            elif kind.mime.startswith('text/'):
                logger.info(f"Detected text file by MIME type: {kind.mime}")
                raw_text = load_text(file_bytes)
            elif kind.mime in ['application/vnd.ms-excel', 
                              'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet']:
                logger.info(f"Detected spreadsheet by MIME type: {kind.mime}")
                raw_text = load_excel(file_bytes)
            elif kind.mime == 'text/csv':
                logger.info("Detected CSV by MIME type")
                raw_text = load_csv(file_bytes)
            elif kind.mime.startswith('video/'):
                logger.info(f"Detected video file by MIME type: {kind.mime}")
                raw_text = load_video(file_bytes)
            elif kind.mime.startswith('audio/'):
                logger.info(f"Detected audio file by MIME type: {kind.mime}")
                raw_text = load_audio(file_bytes)
            else:
                return {
                    "success": False,
                    "error": f"Unsupported file type: {kind.mime}",
                    "content": None
                }
        
        # Normalize the extracted text
        normalized_text = normalize_text(raw_text)
        
        if not normalized_text or normalized_text.startswith("Error"):
            return {
                "success": False,
                "error": raw_text if raw_text.startswith("Error") else "No content extracted",
                "content": None
            }
        
        return {
            "success": True,
            "error": None,
            "content": normalized_text,
            "file_type": get_file_type(filename),
            "filename": uploaded_file.filename
        }
        
    except Exception as e:
        logger.error(f"Error in parse_file: {e}")
        return {
            "success": False,
            "error": f"Failed to process file: {str(e)}",
            "content": None
        }

def get_file_type(filename):
    """
    Helper function to determine file type category
    """
    filename = filename.lower()
    
    if filename.endswith('.pdf'):
        return "pdf"
    elif filename.endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff')):
        return "image"
    elif filename.endswith(('.txt', '.md', '.rtf')):
        return "text"
    elif filename.endswith('.csv'):
        return "csv"
    elif filename.endswith(('.xlsx', '.xls')):
        return "excel"
    elif filename.endswith(('.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv', '.wmv')):
        return "video"
    elif filename.endswith(('.m4a', '.mp3', '.wav', '.aac', '.flac', '.ogg')):
        return "audio"
    else:
        return "unknown"

# Test function for development
async def test_parser():
    """
    Test function to verify parser works (for development only)
    """
    # This would be used during development to test your parser
    pass