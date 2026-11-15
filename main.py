from safety_checker import VisitNodesSafety
from llm_prompts import code_prompt_and_tests
from runner import run_harness
import json

tasks = code_prompt_and_tests()


func = """
def count_vowels(s):
    num = 10
    while num > 3:
        pass
"""

for code, test in tasks:
    print(code)
    print(test)

    safecheck = VisitNodesSafety(code) 
    print(safecheck.errors)
    print(safecheck.warnings)
    run_harness(code, test, 5)