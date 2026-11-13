from code_parser import extract_python_code_from_response
from safety_checker import VisitNodesSafety
import ast

#prompt = "Write python function that adds two numbers and than divide by 2 the result"
prompt = """```python
def numnum():
    # Define the two numbers
    num1 = 10
    num2 = 20
                    
    while num2 > 1:
        num2 += 1
        print("a")

    # Add the two numbers and divide the result by 2
    result = (num1 + num2) / 2

    # Print the result
    print(f"The result is: {result}")

def x(a=[]):
    pass
```
                """

code = extract_python_code_from_response(prompt=prompt)
safecheck = VisitNodesSafety(code)
print(safecheck.errors)
print(safecheck.warnings)