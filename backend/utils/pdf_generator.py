from reportlab.pdfgen import canvas

def generate_pdf(text, filename="brief_output.pdf"):
    c = canvas.Canvas(filename)
    lines = text.split('\n')
    y = 800
    for line in lines:
        c.drawString(50, y, line)
        y -= 20
    c.save()
    return filename
