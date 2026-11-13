from google import genai

API_KEY = None

def get_gemini_response(prompt: str, model: str):

    client = genai.Client(api_key=API_KEY)

    interaction = client.interactions.create(
        model="gemini-3.5-flash-lite", #model
        input=prompt
    )

    return interaction.output_text
