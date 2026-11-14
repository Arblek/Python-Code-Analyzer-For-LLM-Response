from gemini_response import get_gemini_response
import re

def extract_python_code_from_response(prompt: str):
    code = get_gemini_response(prompt)

    match_first_code = re.search(r"```(?:python)?\s*\n(.*?)```", code, re.DOTALL | re.IGNORECASE) #Ensures that if there are multiple alternatives of the code, only the first one is checked
    if match_first_code:
        return match_first_code.group(1)