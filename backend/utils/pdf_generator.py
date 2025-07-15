from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import textwrap


def generate_pdf(text, filename="brief_output.pdf"):
    """
    Generate pdf with nice spacing and formatting - fixed for multi-page
    """
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter
    
    # Page settings
    left_margin = 72  # 1 inch margin
    right_margin = width - 72
    top_margin = height - 72
    bottom_margin = 72
    
    max_width = right_margin - left_margin
    chars_per_line = int(max_width / 6)  # Approximate
    
    lines = text.split('\n')
    y = top_margin
    line_height = 15
    current_font = "Helvetica"  # Track current font
    current_size = 10           # Track current size
    
    def set_font(font_name, size):
        """Helper to set font and track it"""
        nonlocal current_font, current_size
        current_font = font_name
        current_size = size
        c.setFont(font_name, size)
    
    def new_page():
        """Helper to create new page and restore font"""
        nonlocal y
        c.showPage()
        y = top_margin
        c.setFont(current_font, current_size)  # Restore current font
    
    # Add title if text starts with a title
    if lines and lines[0].strip():
        set_font("Helvetica-Bold", 14)
        first_line = lines[0][:50] + "..." if len(lines[0]) > 50 else lines[0]
        c.drawString(left_margin, y, first_line)
        y -= 25
        lines = lines[1:]  # Skip the title line
    
    # Set normal font for body text
    set_font("Helvetica", 10)
    
    for line in lines:
        if not line.strip():  # Empty line - add some space
            y -= line_height * 0.5
            continue
        
        # Check for section headers (lines that end with :)
        if line.strip().endswith(':') and len(line.strip()) < 50:
            # This looks like a section header
            if y < bottom_margin + 40:  # Need space for header + content
                new_page()
            
            set_font("Helvetica-Bold", 11)
            c.drawString(left_margin, y, line.strip())
            y -= line_height * 1.2
            set_font("Helvetica", 10)  # Switch back to normal font
            continue
        
        # Wrap regular content lines
        wrapped_lines = textwrap.wrap(line, width=chars_per_line)
        
        if not wrapped_lines:
            wrapped_lines = [line]
        
        for wrapped_line in wrapped_lines:
            # Check if we need a new page
            if y < bottom_margin:
                new_page()
            
            # Add slight indent for content under headers
            indent = left_margin + 20 if wrapped_line.startswith(('•', '-', '  ')) else left_margin
            c.drawString(indent, y, wrapped_line)
            y -= line_height
    
    c.save()
    return filename