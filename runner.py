import json 
import ast
import subprocess
import tempfile
from pathlib import Path
import sys

HARNESS = r"""
import json
from pathlib import Path
import math

def matches(result, expected):
    numeric = (int, float)
    if (isinstance(result, numeric) and isinstance(expected, numeric)) and not (isinstance(result, bool) and isinstance(expected, bool)):
        return math.isclose(result, expected)
    return result == expected

func_result = None

namespace = {"__name__": "solution"}
source = Path("solution.py").read_text(encoding="utf-8")
exec(compile(source, "solution.py", "exec"), namespace)

tests = json.loads(Path("tests_json.json").read_text())
for test in tests:
    func = namespace.get(test["func"])
    args, kwargs = test.get("args", []), test.get("kwargs", {})

    try:
        result = func(*args, **kwargs)
        if "raises" in test:
            func_result = f"Failed: Expected {test.get("raises")}, but got nothing. Test ran: {test}@0"
        elif matches(result, test.get("expected")):
            func_result = f"Pass@1"
        else:
            func_result = f"Failed: Expected {test.get("expected")}, but got {result}. Test ran: {test}@0"
    except Exception as e:
        if "raises" in test and type(e).__name__ == test.get("raises"):
            func_result = f"Pass@1"
        elif "raises" in test:
            func_result = f"Failed: Expected {test.get("raises")}, but got {type(e).__name__}. Test ran: instead {test}@0"
        else:
            func_result = f"Error: {type(e).__name__}. Test ran: {test}@0"

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
        parsed_json = json.dumps(_load_json_test(tests))
        (tmp/"tests_json.json").write_text(parsed_json, encoding="utf-8")


        try:
            subprocess.run([sys.executable, "-I", "harness.py"], cwd=tmp, timeout=timeout)
        except subprocess.TimeoutExpired:
            results.append(("Timeout Error", 0))

        result_file = tmp / "result.txt"
        if result_file.exists():
            for line in result_file.read_text().splitlines(encoding="utf-8"):
                msg, grade = line.rsplit("@", 1)
                results.append((msg, int(grade)))
        else:
            results.append(("Harness produced no results (code may fail on import)", 0))

        return results
