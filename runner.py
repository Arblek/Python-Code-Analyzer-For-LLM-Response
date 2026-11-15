import json 
import ast
import subprocess
import tempfile
from pathlib import Path
import sys

# func = """
# def count_vowels(s):
#     vowels = "aeiou"
#     # Convert the string to lowercase so the check is case-insensitive
#     s_lower = s.lower()
#     # Count each character in the string if it is in the vowels string
#     return sum(1 for char in s_lower if char in vowels)
#     """

# parsed_tests = '''
# [
#   {"func": "count_vowels", "args": ["hello"], "expected": 2},
#   {"func": "count_vowels", "args": ["AEIOUaeiou"], "expected": 10},
#   {"func": "count_vowels", "args": ["rhythm"], "expected": 0},
#   {"func": "count_vowels", "args": [""], "expected": 0},
#   {"func": "count_vowels", "args": [0], "raises": "TypeError"},
#   {"func": "count_vowels", "args": [-5], "raises": "TypeError"},
#   {"func": "count_vowels", "args": [3.14], "raises": "TypeError"},
#   {"func": "count_vowels", "args": [1000000000000], "raises": "TypeError"},
#   {"func": "count_vowels", "args": [None], "raises": "TypeError"},
#   {"func": "count_vowels", "args": [["a", "e", "i"]], "raises": "TypeError"},
#   {"func": "count_vowels", "args": [{"a": 1}], "raises": "TypeError"},
#   {"func": "count_vowels", "args": [True], "raises": "TypeError"}
# ]
# '''

HARNESS = r"""
import json
from pathlib import Path

func_result = None

namespace = {"__name__": "solution"}
source = Path("solution.py").read_text(encoding="utf-8")
exec(compile(source, "solution.py", "exec"), namespace)

index = 0
tests = json.loads(Path("tests_json.json").read_text())
for test in tests:
    func = namespace.get(test["func"])
    args, kwargs = test.get("args", []), test.get("kwargs", {})

    try:
        result = func(*args, **kwargs)
        if result == test.get("expected"):
            func_result = f"{index} Pass"
        elif "raises" in test:
            func_result = f"{index} Failed: Expected {test.get("raises")}, but got nothing"
        else:
            func_result = f"{index} Failed: Expected {test.get("expected")}, but got {result}"
    except Exception as e:
        if "raises" in test and type(e).__name__ == test.get("raises"):
            func_result = f"{index} Pass"
        elif "raises" in test:
            func_result = f"{index} Failed: Expected {test.get("raises")}, but got {type(e).__name__} instead"
        else:
            func_result = f"{index} Error: {type(e).__name__}"

    index += 1
    with open("result.txt", "a") as file:
        file.write(func_result + "\n")
""" 
def _load_json_test(text: str):
    try:
        return json.loads(text)
    except json.decoder.JSONDecodeError:
        return ast.literal_eval(text)
    
def run_harness(code: str, tests, timeout: int):
    results = []

    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        (tmp/"solution.py").write_text(code, encoding="utf-8")
        (tmp/"harness.py").write_text(HARNESS, encoding="utf-8")
        (tmp/"tests_json.json").write_text(tests, encoding="utf-8")


        try:
            subprocess.run([sys.executable, "-I", "harness.py"], cwd=tmp, timeout=timeout)
        except subprocess.TimeoutExpired:
            results.append("Timeout Error")

        with open((tmp/"result.txt"), "r") as file:
            lines = file.readlines()
            for line in lines:
                results.append(line)

        for line in results:
            print(line)
