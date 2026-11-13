from code_parser import extract_python_code_from_response
import ast

class VisitNodesSafety(ast.NodeVisitor):  
    def __init__(self, code):
        super().__init__()
        self.errors = []

        self.tree = self.check_for_indentations_or_syntax_errors(code) 
        if self.tree:
            self.visit(self.tree)

    def visit_While(self, node: ast.While):
        #Checks if while uses a constant like 1 or True, if so it checks if it has any way of exiting the loop
        if isinstance(node.test, ast.Constant) and bool(node.test.value):
            self._has_exit_conditions(node)

        else:
        #Checks the while loop condition
            condition_variables = {var.id for var in ast.walk(node.test) if isinstance(var, ast.Name)}

            modified_variables = set()
            for var in ast.walk(node):
                if isinstance(var, ast.Assign):
                    for target in var.targets:
                        if isinstance(target, ast.Name):
                            modified_variables.add(target.id)
                elif isinstance(var, ast.AugAssign):
                    modified_variables.add(var.id)

            if not (condition_variables & modified_variables):
                self.errors.append(f"Possible infinit loop! The variables used in condition {condition_variables} are never modified in loop")

        self.generic_visit(node)

    def check_for_indentations_or_syntax_errors(self, code):
        try:
            return ast.parse(code)
        except IndentationError as e:
            self.errors.append(f"Indentation error at line {e.lineno}")
            return None
        except SyntaxError as e:
            self.errors.append(f"Syntax error at line {e.lineno}")
            return None

    def _has_exit_conditions(self, node):
            has_exit = any(isinstance(child_node, (ast.Break, ast.Return, ast.Raise)) for child_node in ast.walk(node)) 

            if not has_exit:
                self.errors.append("Infinite loop")
    def print_error(self):
        print(self.errors)