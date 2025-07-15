import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from backend.utils.pdf_generator import generate_pdf

sample_text = """
Objective: Promote eco-friendly notebooks
Audience: Students and young professionals
Messaging: Sustainability, Simplicity, Style
Content Suggestions: Instagram Reels, Campus Ambassadors
KPIs: Engagement, Sales Uplift, Brand Awareness
"""

pdf_path = generate_pdf(sample_text)
print(f"PDF successfully saved at: {pdf_path}")
