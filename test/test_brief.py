import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.agents.briefer_agent import generate_brief

sample_text = """
We are launching a new line of eco-friendly notebooks aimed at students and young professionals.
The product uses recycled paper, minimalist design, and carbon-neutral shipping.
"""

brief = generate_brief(sample_text)
print("\nGenerated Brief:\n")
print(brief)
