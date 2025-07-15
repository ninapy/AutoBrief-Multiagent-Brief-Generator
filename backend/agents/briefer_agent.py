import os
from openai import OpenAI
from dotenv import load_dotenv
import traceback

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT_TEMPLATE = """
You are a creative brief writer. Based on the following input, return a structured brief **in {language}**.

Include: 
- Objective
- Audience
- Messaging
- Content Suggestions
- KPIs
"""

def generate_brief(user_text: str, language: str = "English") -> str:
    try:
        system_prompt = SYSTEM_PROMPT_TEMPLATE.format(language=language)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_text}
            ],
            temperature=0.4
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        traceback.print_exc()
        return f"Error generating brief: {str(e)}"
