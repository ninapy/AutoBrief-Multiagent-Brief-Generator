import io
import pdfplumber
from PIL import Image
import pytesseract
import logging
import pandas as pd

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_pdf(file_bytes):
    """
    Extract text from PDF file bytes using pdfplumber
    """
    try:
        # Create a BytesIO object from the file bytes
        pdf_file = io.BytesIO(file_bytes)
        
        text_content = []
        
        with pdfplumber.open(pdf_file) as pdf:
            for page_num, page in enumerate(pdf.pages):
                try:
                    # Extract text from each page
                    page_text = page.extract_text()
                    if page_text:
                        text_content.append(f"--- Page {page_num + 1} ---")
                        text_content.append(page_text.strip())
                except Exception as e:
                    logger.warning(f"Could not extract text from page {page_num + 1}: {e}")
                    continue
        
        if not text_content:
            return "No text content found in PDF"
        
        return "\n\n".join(text_content)
    
    except Exception as e:
        logger.error(f"Error processing PDF: {e}")
        return f"Error processing PDF: {str(e)}"

def load_image(file_bytes):
    """
    Extract text from image file bytes using OCR (pytesseract)
    """
    try:
        # Create PIL Image from bytes
        image = Image.open(io.BytesIO(file_bytes))
        
        # Convert to RGB if necessary (some formats might be RGBA or grayscale)
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Use pytesseract to extract text
        extracted_text = pytesseract.image_to_string(image)
        
        # Clean up the extracted text
        cleaned_text = extracted_text.strip()
        
        if not cleaned_text:
            return "No text found in image"
        
        return cleaned_text
    
    except Exception as e:
        logger.error(f"Error processing image: {e}")
        return f"Error processing image: {str(e)}"

def load_text(file_bytes):
    """
    Load plain text from file bytes
    """
    try:
        # Try different encodings
        encodings = ['utf-8', 'utf-16', 'latin-1', 'ascii']
        
        for encoding in encodings:
            try:
                text = file_bytes.decode(encoding)
                return text.strip()
            except UnicodeDecodeError:
                continue
        
        # If all encodings fail, try with error handling
        text = file_bytes.decode('utf-8', errors='replace')
        return text.strip()
    
    except Exception as e:
        logger.error(f"Error processing text file: {e}")
        return f"Error processing text file: {str(e)}"
    
def load_csv(file_bytes):
    """
    Extract data from CSV file bytes and convert to readable text
    """
    try:
        # Create StringIO from bytes
        csv_data = io.StringIO(file_bytes.decode('utf-8'))
        
        # Read CSV with pandas
        df = pd.read_csv(csv_data)
        
        # Convert to a readable text format
        text_content = []
        
        # Add basic info about the data
        text_content.append(f"CSV Data Summary:")
        text_content.append(f"Rows: {len(df)}, Columns: {len(df.columns)}")
        text_content.append(f"Column Names: {', '.join(df.columns.tolist())}")
        text_content.append("")
        
        # Add sample of the data (first 10 rows)
        text_content.append("Sample Data (first 10 rows):")
        sample_data = df.head(10).to_string(index=False)
        text_content.append(sample_data)
        
        # Add summary statistics for numeric columns
        numeric_cols = df.select_dtypes(include=['number']).columns
        if len(numeric_cols) > 0:
            text_content.append("")
            text_content.append("Numeric Column Summary:")
            for col in numeric_cols:
                stats = df[col].describe()
                text_content.append(f"{col}: Mean={stats['mean']:.2f}, Min={stats['min']:.2f}, Max={stats['max']:.2f}")
        
        return "\n".join(text_content)
    
    except Exception as e:
        logger.error(f"Error processing CSV: {e}")
        return f"Error processing CSV: {str(e)}"

def load_excel(file_bytes):
    """
    Extract data from Excel file bytes and convert to readable text
    """
    try:
        # Create BytesIO object
        excel_file = io.BytesIO(file_bytes)
        
        # Read all sheets
        excel_data = pd.read_excel(excel_file, sheet_name=None)  # None reads all sheets
        
        text_content = []
        text_content.append("Excel File Summary:")
        text_content.append(f"Number of sheets: {len(excel_data)}")
        text_content.append("")
        
        # Process each sheet
        for sheet_name, df in excel_data.items():
            text_content.append(f"=== Sheet: {sheet_name} ===")
            text_content.append(f"Rows: {len(df)}, Columns: {len(df.columns)}")
            text_content.append(f"Column Names: {', '.join(df.columns.astype(str).tolist())}")
            text_content.append("")
            
            # Add sample data (first 5 rows per sheet to avoid too much text)
            text_content.append("Sample Data (first 5 rows):")
            sample_data = df.head(5).to_string(index=False)
            text_content.append(sample_data)
            
            # Add summary for numeric columns
            numeric_cols = df.select_dtypes(include=['number']).columns
            if len(numeric_cols) > 0:
                text_content.append("")
                text_content.append("Numeric Summary:")
                for col in numeric_cols:
                    if not df[col].isna().all():  # Skip if all values are NaN
                        stats = df[col].describe()
                        text_content.append(f"{col}: Mean={stats['mean']:.2f}, Min={stats['min']:.2f}, Max={stats['max']:.2f}")
            
            text_content.append("")  # Space between sheets
        
        return "\n".join(text_content)
    
    except Exception as e:
        logger.error(f"Error processing Excel: {e}")

def normalize_text(text):
    """
    Helper function to clean and normalize extracted text
    """
    if not text:
        return ""
    
    # Remove excessive whitespace
    lines = text.split('\n')
    cleaned_lines = []
    
    for line in lines:
        cleaned_line = line.strip()
        if cleaned_line:  # Only keep non-empty lines
            cleaned_lines.append(cleaned_line)
    
    return '\n'.join(cleaned_lines)