from gemini_response import get_gemini_response
import ast
import re

def validate_code(candidate_code: str):
    try:
        ast.parse(candidate_code)
        return True
    except SyntaxError:
        return False

def extract_python_code_from_response(prompt: str):
    code = get_gemini_response(prompt, "gemini-3.5-flash-lite")

    match_first_code = re.search(r"```(?:python)?\s*\n(.*?)```", code, re.DOTALL | re.IGNORECASE) #Ensures that if there are multiple alternatives of the code, only the first one is checked
    if match_first_code:
        #lines = match_first_code.group(1).splitlines()
        return match_first_code.group(1)
    # else:
    #     lines = prompt.splitlines()
        
    # for line_start, line in enumerate(lines):
    #     if line.lstrip().startswith(("import ", "from ", "def ", "class ", "")):
    #         for line_end in range(len(lines), line_start, -1):
    #             candidate = "\n".join(lines[line_start:line_end])
    #             if validate_code(candidate_code=candidate):
    #                 return candidate

    