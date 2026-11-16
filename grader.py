from runner import run_harness

def grade(code, tests, timeout = 5):
    grades = run_harness(code, tests, 5)

    total_grades = 0
    pass_grades = 0
    failed_tests = []
    for msg, grade in grades:
        if grade == 1:
            pass_grades += 1
        else:
            failed_tests.append(msg)
        total_grades += 1

    points_per_test = 100 / total_grades
    final_grade = points_per_test * pass_grades

    return final_grade, total_grades, pass_grades, failed_tests
    