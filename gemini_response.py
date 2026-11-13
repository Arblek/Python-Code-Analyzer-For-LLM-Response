from google import genai
import os
from dotenv import load_dotenv

load_dotenv()
def get_gemini_response(prompt: str, model: str):

    client = genai.Client(api_key=os.getenv("API_KEY"))

    interaction = client.interactions.create(
        model=model,
        input=prompt
    )

    return interaction.output_text
