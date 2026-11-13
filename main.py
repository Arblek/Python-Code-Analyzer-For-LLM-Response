from code_parser import extract_python_code_from_response
from safety_checker import VisitNodesSafety
import ast

#prompt = "Write python function that adds two numbers and than divide by 2 the result"
prompt = """```python
def numnum():
    # Define the two numbers
    num1 = 10
    num2 = 20
                    
    while num1 > 3 and num2 > 4:
        print("a")
        num2 = 0

    # Add the two numbers and divide the result by 2
    result = (num1 + num2) / 2

    # Print the result
    print(f"The result is: {result}")
```
                """

code = extract_python_code_from_response(prompt=prompt)
safecheck = VisitNodesSafety(code)
safecheck.print_error() 