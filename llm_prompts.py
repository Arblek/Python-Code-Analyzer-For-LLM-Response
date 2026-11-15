import json 
from code_parser import extract_python_code_from_response
from gemini_response import get_gemini_response

def code_prompt_and_tests():
    spec = json.load(open("prompt.json", encoding="utf-8"))

    result = []
    for task in spec:
        sign = task["signature"]
        des = task["description"]
        func = task["func"]

        prompt_code = f"Write a Python function {sign} that {des}."

        prompt_test = f"""You are writing test cases for a Python function. You will not see the implementation.
        Function: {sign}, which {des}.

        Return ONLY a JSON array. Each item must have "func" and "args", plus either
        "expected" or "raises" (an exception class name). Use only JSON-serializable values.
        Do not include explanations.

        Example format: {{"func": "{func}", "args": [1, 2], "expected": 1.5}}

        Write at least 12 cases covering: normal values, zero, negatives, floats, very large
        numbers, mixed int and float, and several invalid types (None, strings, lists)."""

        code = extract_python_code_from_response(prompt_code)
        tests = get_gemini_response(prompt_test)

        result.append((code, tests))

    return result