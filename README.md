# Python Code Analyzer for LLM Responses

A command-line tool that asks an LLM (Google Gemini) to write Python functions, then checks and grades the generated code automatically. It answers the question: *is this AI-written code actually correct, and is it safe to run?*

For each task, the tool:

1. **Generates** the function from a short spec using Gemini.
2. **Generates** a separate set of test cases (the model writing the tests never sees the implementation).
3. **Analyzes** the code statically before running it, and rejects code with serious problems.
4. **Runs** the code against the tests in an isolated subprocess with a timeout.
5. **Grades** the result as the percentage of tests passed and prints any failures.

## Static safety checks

Before any generated code is run, it is parsed into an AST and checked for:

- Syntax and indentation errors
- Infinite `while` loops (`while True` with no exit) and loops whose condition variables are never changed inside the loop
- Mutable default arguments (`list`, `dict`, `set`) in function definitions
- Unreachable code after `return`, `raise`, `break` or `continue`

If any check fails, the code is marked as broken and the tests are skipped.

## Example output

Results are printed with [rich](https://github.com/Textualize/rich): the generated code, then either a list of failed tests with `Tests passed X/Y` and a grade out of 100, or the list of static errors.

## Setup

Requires Python 3.12 or newer and a Gemini API key.

```bash
pip install -r requirements.txt
```

Create a `.env` file in the project folder:

```
API_KEY=your_gemini_api_key
```

## Usage

Describe the functions you want in `prompt.json`:

```json
[
  {
    "func": "is_even",
    "signature": "is_even(n)",
    "description": "returns True if the integer n is even, otherwise False"
  }
]
```

Then run:

```bash
python main.py
```

The included `prompt.json` has sample tasks such as `add_half`, `is_even`, `reverse_string` and `is_palindrome`.

## Project structure

```
main.py             # runs every task and prints the report
llm_prompts.py      # builds prompts for the code and the tests, calls the model
gemini_response.py  # Gemini API wrapper (reads API_KEY from .env)
code_parser.py      # extracts the first Python code block from a model reply
safety_checker.py   # AST-based static checks
runner.py           # runs the code and tests in a temp directory subprocess
grader.py           # turns test results into a score
prompt.json         # task definitions: function name, signature, description
```

## Important limitations

- **Generated code is executed on your machine.** It runs in a separate subprocess inside a temporary folder with a 5-second timeout, but this is **not a security sandbox**. The static checks look for common bugs, not malicious code. Run it in a container or virtual machine if you use untrusted prompts.
- **The tests are also written by an LLM**, so a high grade means the code agrees with the model's tests, not that it is proven correct.
- Known issue: line numbers reported by `safety_checker.py` can be inaccurate (see the TODO in `main.py`).
