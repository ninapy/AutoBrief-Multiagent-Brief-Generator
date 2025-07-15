import openai

def generate_brief(text: str):
    prompt = f"""
    You are a creative brief writer. Based on the following input, return a structured brief:

    ===
    {text}
    ===

    Include: Objective, Audience, Messaging, Content Suggestions, KPIs
    """

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )

    return response['choices'][0]['message']['content']
