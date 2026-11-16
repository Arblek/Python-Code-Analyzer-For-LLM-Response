from safety_checker import VisitNodesSafety
from llm_prompts import code_prompt_and_tests
from grader import grade
from rich.console import Console
from rich import print

console = Console()
tasks = code_prompt_and_tests()

#TODO: Fix line bug in safety_checker.py
#TODO: runner.py reads result.txt unconditionally. If the very first test hangs, the file doesn’t exist and you get a FileNotFoundError instead of a clean “Timeout Error”.

task_counter = 1
for code, test in tasks:
    console.rule(characters="=", style="blue")
    console.rule(f"{task_counter}", characters="=", style="blue")
    console.rule(characters="=", style="blue")

    console.rule("CODE", characters="=", style="white")
    print(code)
    console.rule(characters="=", style="white")

    safecheck = VisitNodesSafety(code) 

    if not safecheck.errors:
        final_grade, total_grades, pass_grades, failed_tests = grade(code, test, 5)
        if failed_tests:
            console.rule("[bold red] FAILED TESTS [/bold red]", characters="=", style="red")
            print(" ")

            for test in failed_tests:
                print(f"[bold red] {test} [/bold red]")
            
            print(" ")
            console.rule(characters="=")
            print(f"[bold green] Tests passed {pass_grades}/{total_grades}: {final_grade} [/bold green]")
        print(f"[bold green] Tests grade: {final_grade} [/bold green]")
    else:
        console.rule("[bold red]THE CODE IS BROKEN[/bold red]", characters="=", style="red")
        errors = safecheck.errors
        for error in errors:
            print(f"[bold red] {error} [/bold red]")
        console.rule(characters="=", style="red")

    task_counter += 1
    console.rule(characters="=", style="blue")
    console.rule(characters="=", style="blue")
    console.rule(characters="=", style="blue")
