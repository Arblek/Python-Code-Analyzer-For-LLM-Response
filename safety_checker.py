import ast

class VisitNodesSafety(ast.NodeVisitor):  
    def __init__(self, code):
        super().__init__()
        self.errors = []

    
        self.tree = self.check_for_indentations_or_syntax_errors(code) 
        if self.tree:
            self.visit(self.tree)

    def visit_While(self, node: ast.While):
        has_exit = any(isinstance(n, (ast.Break, ast.Return, ast.Raise))
                    for n in ast.walk(node))
        if not has_exit:
            if isinstance(node.test, ast.Constant):
                if node.test.value:
                    self.errors.append(f"Infinite loop at line {node.lineno}")
            else:
                condition_vars = self._names_in(node.test)
                modified_vars = self._modified_variables(node)
                if not any(self._is_modified(name, modified_vars) for name in condition_vars):
                    self.errors.append(
                        f"Possible infinite loop at line {node.lineno}: "
                        f"{sorted(condition_vars)} never modified in loop")

        self.generic_visit(node)


    def visit_FunctionDef(self, node: ast.FunctionDef):
        mutable_args = self.check_for_mutable_args_in_func_def(node)
        unreachable_code = self.check_for_unreachable_code(node)

        if unreachable_code:
            self.errors.append(f"Unreachable code at line {node.lineno}")

        if mutable_args:
            is_mutable, data_type = self.check_for_mutable_args_in_func_def(node)
            if is_mutable:
                self.errors.append(f"Mutable {data_type} argument in function definition at line: {node.lineno}")

        self.generic_visit(node)
    visit_AsyncFunctionDef = visit_FunctionDef      

    def _is_modified(self, name, modified_vars):
        return any(name == m or name.startswith(m + ".") for m in modified_vars)
    
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
                modified_vars |= self._names_in(target)

        return modified_vars

    def _names_in(self, node: ast.While):
        bases = {id(n.value) for n in ast.walk(node) if isinstance(n, ast.Attribute) and isinstance(n.value, ast.Name)}
        names = set()

        for name in ast.walk(node):
            if isinstance(name, ast.Name) and id(name) not in bases:
                names.add(name.id)
            elif isinstance(name, ast.Attribute):
                names.add(ast.unparse(name))

        return names   
          
    def check_for_mutable_args_in_func_def(self, node):
        all_defaults = node.args.defaults + [kwargs for kwargs in node.args.kw_defaults]
        for arg in all_defaults:                                                      
            if isinstance(arg, ast.List):
                return True, "list"
            elif isinstance(arg, ast.Dict):
                return True, "dictionary"
            elif isinstance(arg, ast.Set):
                return True, "set"
        return False, None

    def check_for_unreachable_code(self, node):
        for subnode in ast.walk(node):
            for field in ("body", "orelse", "finalbody"):                                            
                statements = getattr(subnode, field, None)
                if not isinstance(statements, list):
                    continue

                has_terminated = False
                for statement in statements:
                    if has_terminated:
                        return True
                    if isinstance(statement, ((ast.Break, ast.Return, ast.Raise, ast.Continue))):                 
                        has_terminated = True
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