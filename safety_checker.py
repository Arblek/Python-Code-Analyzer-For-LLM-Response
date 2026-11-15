from code_parser import extract_python_code_from_response
import ast

class VisitNodesSafety(ast.NodeVisitor):  
    def __init__(self, code):
        super().__init__()
        self.errors = []
        self.warnings = []

        self.tree = self.check_for_indentations_or_syntax_errors(code) 
        if self.tree:
            self.visit(self.tree)

    def visit_While(self, node: ast.While):
        variables = self._names_in(node)
        variables_modified = self._modified_variables(node)

        has_exit = any(isinstance(n, (ast.Break, ast.Return, ast.Raise))
                    for n in ast.walk(node))
        if not has_exit:
            if isinstance(node.test, ast.Constant) and node.test.value:
                self.errors.append(f"Infinite loop at line {node.lineno}")
            else:
                if not (self._names_in(node.test) & self._modified_variables(node)):
                    self.errors.append(f"Possible infinit loop! The variables used in condition {self._names_in(node.test)} at line {node.lineno} are never modified in loop")

        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        mutable_args = self.check_for_mutable_args_in_func_def(node)
        unreachable_code = self.check_for_unreachable_code(node)

        if unreachable_code:
            is_unreachable = self.check_for_unreachable_code(node)
            if is_unreachable:
                self.warnings.append(f"Unreachable code at line {node.lineno}")

        if mutable_args:
            is_mutable, data_type = self.check_for_mutable_args_in_func_def(node)
            if is_mutable:
                self.warnings.append(f"Mutable {data_type} argument in function definition at line: {node.lineno}")

        self.generic_visit(node)        

    def visit_FunctionDef(self, node: ast.FunctionDef):
        mutable_args = self.check_for_mutable_args_in_func_def(node)
        unreachable_code = self.check_for_unreachable_code(node)

        if unreachable_code:
            is_unreachable = self.check_for_unreachable_code(node)
            if is_unreachable:
                self.warnings.append(f"Unreachable code at line {node.lineno}")

        if mutable_args:
            is_mutable, data_type = self.check_for_mutable_args_in_func_def(node)
            if is_mutable:
                self.warnings.append(f"Mutable {data_type} argument in function definition at line: {node.lineno}")

        self.generic_visit(node)


    def _modified_variables(self, node: ast.While):
        modified_vars = set()

        for modified in ast.walk(node):
            if isinstance(modified, ast.Assign):
                targets = modified.targets
            elif isinstance(modified, (ast.AugAssign, ast.AnnAssign)):
                targets = [modified.target]
            else:
                continue
            for target in targets:
                for sub in ast.walk(target):
                    if isinstance(sub, ast.Name):
                        modified_vars.add(sub.id)
                    elif isinstance(sub, ast.Attribute):
                        modified_vars.add(sub.attr)

        return modified_vars

    def _names_in(self, node: ast.While):
        names = set()

        for name in ast.walk(node):
            if isinstance(name, ast.Name):
                names.add(name.id)
            elif isinstance(name, ast.Attribute):
                names.add(name.attr)

        return names   
          
    def check_for_mutable_args_in_func_def(self, node):
        all_defaults = node.args.defaults + [kwargs for kwargs in node.args.kw_defaults]
        for arg in all_defaults:                                                      #Check for mutable arguments in function definition
            if isinstance(arg, ast.List):
                return True, "list"
            elif isinstance(arg, ast.Dict):
                return True, "dictionary"
            elif isinstance(arg, ast.Set):
                return True, "set"
        return False

    def check_for_unreachable_code(self, node):
        for subnode in ast.walk(node):
            for field in ("body", "orelse", "finalbody"):                                           #Checks for unreachable code 
                statements = getattr(subnode, field, None)
                if not isinstance(statements, list):
                    continue
                for statement in statements:
                    if isinstance(statement, ((ast.Break, ast.Return, ast.Raise))):                 #Sets the has_terminated to True if it encounters a break, return or raise keyword
                        return True
        return False

    def check_for_indentations_or_syntax_errors(self, code):
        try:
            return ast.parse(code)
        except IndentationError as e:
            self.errors.append(f"Indentation error at line {e.lineno}")
            return None
        except SyntaxError as e:
            self.errors.append(f"Syntax error at line {e.lineno}")
            return None
        except TypeError:
            self.errors.append("No code found")