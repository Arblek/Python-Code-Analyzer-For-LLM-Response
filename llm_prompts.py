import json 
from code_parser import extract_python_code_from_response
from gemini_response import get_gemini_response

def code_prompt_and_tests():
    spec = json.load(open("prompt.json", encoding="utf-8"))

    prompt_code = f"Write a Python function {spec['signature']} that {spec['description']}."

    prompt_test = f"""You are writing test cases for a Python function. You will not see the implementation.
    Function: {spec['signature']}, which {spec['description']}.

    Return ONLY a JSON array. Each item must have "func" and "args", plus either
    "expected" or "raises" (an exception class name). Use only JSON-serializable values.
    Do not include explanations.

    Example format: {{"func": "{spec['func']}", "args": [1, 2], "expected": 1.5}}

    Write at least 12 cases covering: normal values, zero, negatives, floats, very large
    numbers, mixed int and float, and several invalid types (None, strings, lists)."""

    code = extract_python_code_from_response(prompt_code)
    tests = get_gemini_response(prompt_test)

    return code, tests