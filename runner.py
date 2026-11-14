import json 

# func = """
# def add_half(a, b):
#     return (a + b) / 2
#     """

# parsed_tests = json.loads('''
# [
#   {"func": "add_half", "args": [2, 4], "expected": 3.0},
#   {"func": "add_half", "args": [0, 0], "expected": 0.0},
#   {"func": "add_half", "args": [-2, -4], "expected": -3.0},
#   {"func": "add_half", "args": [-5, 5], "expected": 0.0},
#   {"func": "add_half", "args": [1.5, 2.5], "expected": 2.0},
#   {"func": "add_half", "args": [1, 2.5], "expected": 1.75},
#   {"func": "add_half", "args": [1000000000000, 3000000000000], "expected": 2000000000000.0},
#   {"func": "add_half", "args": [1, "2"], "raises": "TypeError"},
#   {"func": "add_half", "args": ["1", "2"], "raises": "TypeError"},
#   {"func": "add_half", "args": [null, 5], "raises": "TypeError"},
#   {"func": "add_half", "args": [[1], 2], "raises": "TypeError"},
#   {"func": "add_half", "args": [1], "raises": "TypeError"},
#   {"func": "add_half", "args": [2, 4], "expected": 4},
#   {"func": "add_half", "args": [2, 4], "raises": "TypeError"},
#   {"func": "add_half", "args": ["a", "b"], "raises": "ValueError"},
#   {"func": "add_half", "args": [1], "expected": 1},
#   {"func": "add_halfs", "args": [2, 4], "expected": 3}
# ]
# ''')

def run(code: str, tests: list[dict]):
    namespace = {"__name__": "solution"}

    exec(compile(code, "solution.py", "exec"), namespace)

    index = 0
    for test in tests:
        func = namespace.get(test["func"])
        args, kwargs = test.get("args", []), test.get("kwargs", {})

        try:
            result = func(*args, **kwargs)
            if result == test.get("expected"):
                print(index, "Pass")
            elif "raises" in test:
                print(index, f"Failed: Expected {test.get("raises")}, but got nothing")
            else:
                print(index, f"Failed: Expected {test.get("expected")}, but got {result}")
        except Exception as e:
            if "raises" in test and type(e).__name__ == test.get("raises"):
                print(index, "Pass")
            elif "raises" in test:
                print(index, f"Failed: Expected {test.get("raises")}, but got {type(e).__name__} instead")
            else:
                print(index, f"Error: {type(e).__name__}")

        index += 1
        
        

#run(func, parsed_tests)