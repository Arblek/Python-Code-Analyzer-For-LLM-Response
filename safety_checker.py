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
        self.check_for_infinite_while_condition(node)
        self.check_for_infinite_while_constant(node)

        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef):
        self.check_for_mutable_args_in_func_def(node)
        self.check_for_unreachable_code(node)
        
        self.generic_visit(node)

    def check_for_infinite_while_constant(self, node):
        if isinstance(node.test, ast.Constant) and bool(node.test.value):        #Checks if while uses a constant like 1 or True, if so it checks if it has any way of exiting the loop
            has_exit = any(isinstance(child_node, (ast.Break, ast.Return, ast.Raise)) for child_node in ast.walk(node)) 

            if not has_exit:
                self.errors.append("Infinite loop")

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
                self.errors.append(f"Possible infinit loop! The variables used in condition {condition_variables} are never modified in loop")
                
    def check_for_mutable_args_in_func_def(self, node):
        for arg in node.args.defaults:                                                      #Check for mutable arguments in function definition
            if isinstance(arg, ast.List):
                self.warnings.append("Mutable list argument in function definition")
            elif isinstance(arg, ast.Dict):
                self.warnings.append("Mutable dictionary argument in function definition")
            elif isinstance(arg, ast.Set):
                self.warnings.append("Mutable set argument in function definition")

    def check_for_unreachable_code(self, node):
        has_terminated = False
        for statement in node.body:                                                         #Checks for unreachable code 
            if has_terminated:
                line = getattr(statement, "lineno", "unknown")                              #Gets the line of the unreachable code
                self.warnings.append(f"Unreachable code at line {line}")
                break                                                                       #Breaks after the next line after the break, return or raise keyword
            if isinstance(statement, ((ast.Break, ast.Return, ast.Raise))):                 #Sets the has_terminated to True if it encounters a break, return or raise keyword
                has_terminated = True

    def check_for_indentations_or_syntax_errors(self, code):
        try:
            return ast.parse(code)
        except IndentationError as e:
            self.errors.append(f"Indentation error at line {e.lineno}")
            return None
        except SyntaxError as e:
            self.errors.append(f"Syntax error at line {e.lineno}")
            return None

