from runner import run_harness, _load_json_test


def grade(code, tests, timeout=5):
    try:
        total_tests = len(_load_json_test(tests))
    except Exception as e:
        return 0.0, 0, 0, [f"Could not parse the tests: {type(e).__name__}: {e}"]

    if total_tests == 0:
        return 0.0, 0, 0, ["No tests to run"]

    results = run_harness(code, tests, timeout)

    pass_grades = sum(1 for _, score in results if score == 1)
    failed_tests = [msg for msg, score in results if score != 1]
    final_grade = 100 * pass_grades / total_tests

    return final_grade, total_tests, pass_grades, failed_tests