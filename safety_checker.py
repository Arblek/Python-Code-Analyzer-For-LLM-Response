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
        condition_result = self.check_for_infinite_while_condition(node)

        if self.check_for_infinite_while_constant(node):
            self.errors.append("Infinite loop")
        if condition_result:
            is_infinite, condition_variables = condition_result
            self.errors.append(f"Possible infinit loop! The variables used in condition {condition_variables} are never modified in loop")

        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef):
        mutable_args = self.check_for_unreachable_code(node)
        unreachable_code = self.check_for_mutable_args_in_func_def(node)

        if unreachable_code:
            is_unreachable, line = self.check_for_unreachable_code(node)
            if is_unreachable:
                self.warnings.append(f"Unreachable code at line {line}")
        if mutable_args:
            is_mutable, data_type = self.check_for_mutable_args_in_func_def(node)
            if is_mutable:
                self.warnings.append(f"Mutable {data_type} argument in function definition")

        self.generic_visit(node)

    def check_for_infinite_while_constant(self, node):
        if isinstance(node.test, ast.Constant) and bool(node.test.value):        #Checks if while uses a constant like 1 or True, if so it checks if it has any way of exiting the loop
            has_exit = any(isinstance(child_node, (ast.Break, ast.Return, ast.Raise)) for child_node in ast.walk(node)) 

            if not has_exit:
                return True
        return False

    def check_for_infinite_while_condition(self, node):
        #Checks the while loop condition
            condition_variables = {var.id for var in ast.walk(node.test) if isinstance(var, ast.Name)}

            modified_variables = set()                              #Set to store the variables that are modified in the loop body
            for var in ast.walk(node):
                if isinstance(var, ast.Assign):                     #Checks is there is an assigment e.g:  x = 10
                    for target in var.targets:                      #A variable can be assigned like this a, b, c = 10 thats why we use a for loop here
                        if isinstance(target, ast.Name):            #If it finds a variable it gets added to the modified_variables set()
                            modified_variables.add(target.id)
                elif isinstance(var, ast.AugAssign):                #This elif is used to catch the case where a variable if modified like this x += 1
                    modified_variables.add(var.target.id)

            if not (condition_variables & modified_variables):      #Cross references the sets 
                return True, condition_variables
            return False
                
    def check_for_mutable_args_in_func_def(self, node):
        for arg in node.args.defaults:                                                      #Check for mutable arguments in function definition
            if isinstance(arg, ast.List):
                return True, "list"
            elif isinstance(arg, ast.Dict):
                return True, "dictionary"
            elif isinstance(arg, ast.Set):
                return True, "set"
        return False

    def check_for_unreachable_code(self, node):
        has_terminated = False
        for statement in node.body:                                                         #Checks for unreachable code 
            if has_terminated:
                line = getattr(statement, "lineno", "unknown")                              #Gets the line of the unreachable code
                return True, line                                                                     #Breaks after the next line after the break, return or raise keyword
            if isinstance(statement, ((ast.Break, ast.Return, ast.Raise))):                 #Sets the has_terminated to True if it encounters a break, return or raise keyword
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

