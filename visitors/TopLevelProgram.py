import ast

LabeledInstruction = tuple[str, str]


class TopLevelProgram(ast.NodeVisitor):
    """We supports assignments and input/print calls"""

    def __init__(self, entry_point, vars, lable=0) -> None:
        super().__init__()
        self.funcDef = list()
        self.funcNames = list()
        self.instructions = list()
        self.record_instruction('NOP1', label=entry_point)
        self.should_save = True
        self.current_variable = None
        self.elem_id = lable
        self.vars = vars

    def finalize(self):
        self.instructions.append((None, '.END'))
        return (self.instructions, self.funcDef, self.funcNames)

    ####
    # Handling Assignments (variable = ...)
    ####

    def visit_Assign(self, node):
        if (isinstance(node.value, ast.Call)
                and node.value.func.id in self.funcNames):
            self.record_instruction(f'SUBSP {len(node.value.args)*2+2},i')

            for i, a in enumerate(node.value.args):
                if a.id in self.vars:
                    self.record_instruction(f'LDWA {self.vars[a.id]},d')
                else:
                    self.record_instruction(f'LDWA {a.id},d')
                self.record_instruction(f'STWA {i*2},s')

            self.record_instruction(f'CALL {node.value.func.id}')
            self.record_instruction(f'ADDSP {len(node.value.args)*2},i')
            self.record_instruction(f'LDWA 0,s')
            if node.targets[0].id in self.vars:
                self.record_instruction(
                    f'STWA {self.vars[node.targets[0].id]},d')
            else:
                self.record_instruction(
                    f'STWA {node.targets[0].id},d')
            self.record_instruction(f'ADDSP 2,i')

        else:
            temp = self.rename(node.targets[0].id)
            if not (temp[0] == "_" and temp[1:].isupper()):
                # remembering the name of the target
                self.current_variable = temp
                # visiting the left part, now knowing where to store the result
                self.visit(node.value)
                if self.should_save:
                    self.record_instruction(f'STWA {self.current_variable},d')
                else:
                    self.should_save = True
                self.current_variable = None

    def visit_Constant(self, node):
        self.record_instruction(f'LDWA {node.value},i')

    def visit_Name(self, node):
        self.record_instruction(f'LDWA {node.id},d')

    def visit_BinOp(self, node):
        self.access_memory(node.left, 'LDWA')
        if isinstance(node.op, ast.Add):
            self.access_memory(node.right, 'ADDA')
        elif isinstance(node.op, ast.Sub):
            self.access_memory(node.right, 'SUBA')
        else:
            raise ValueError(f'Unsupported binary operator: {node.op}')

    def visit_Call(self, node):
        match node.func.id:
            case 'int':
                # Let's visit whatever is casted into an int
                self.visit(node.args[0])
            case 'input':
                # We are only supporting integers for now
                self.record_instruction(f'DECI {self.current_variable},d')
                self.should_save = False  # DECI already save the value in memory
            case 'print':
                # We are only supporting integers for now
                self.record_instruction(f'DECO {node.args[0].id},d')
            case _:
                if (isinstance(node, ast.Call)
                        and node.func.id in self.funcNames):

                    if node.args:
                        self.record_instruction(f'SUBSP {len(node.args)*2},i')

                    for i, a in enumerate(node.args):
                        if a.id in self.vars:
                            self.record_instruction(
                                f'LDWA {self.vars[a.id]},d')
                        else:
                            self.record_instruction(
                                f'LDWA {a.id},d')
                        self.record_instruction(f'STWA {i*2},s')

                    self.record_instruction(f'CALL {node.func.id}')
                    if node.args:
                        self.record_instruction(f'ADDSP {len(node.args)*2},i')

    ####
    # Handling While loops (only variable OP variable)
    ####

    def visit_While(self, node, loop_id=''):
        loop_id = self.identify()
        inverted = self.conditons()
        # left part can only be a variable
        self.access_memory(node.test.left, 'LDWA', label=f't_{loop_id}')
        # right part can only be a variable
        self.access_memory(node.test.comparators[0], 'CPWA')
        # Branching is condition is not true (thus, inverted)
        self.record_instruction(
            f'{inverted[type(node.test.ops[0])]} end_l_{loop_id}')
        # Visiting the body of the loop
        for contents in node.body:
            self.visit(contents)
        self.record_instruction(f'BR t_{loop_id}')
        # Sentinel marker for the end of the loop
        self.record_instruction(f'NOP1', label=f'end_l_{loop_id}')

    def visit_If(self, node):
        loop_id = self.identify()
        inverted = self.conditons()
        self.access_memory(node.test.left, 'LDWA', label=f'if_{loop_id}')
        self.access_memory(node.test.comparators[0], 'CPWA')
        
        if node.orelse != []:
            # compare branch 
            if ast.If in [type(i) for i in node.orelse]:  # there is an else if
                self.record_instruction(
                    f'{inverted[type(node.test.ops[0])]} if_{loop_id + 1}')
            else:
                self.record_instruction(
                    f'{inverted[type(node.test.ops[0])]} else_{loop_id}')
            

            for contents in node.body:
                self.visit(contents)

            # end branch
            if ast.If in [type(i) for i in node.orelse]:  # there is an else if
               self.record_instruction(f'BR end_{loop_id}')
               
            else: # there is an else
                self.record_instruction(f'BR end_{loop_id}')
                self.record_instruction(f'NOP1', label=f'else_{loop_id}')
            for contents in node.orelse:
                self.visit(contents)
        else:
            self.record_instruction(
                    f'{inverted[type(node.test.ops[0])]} end_{loop_id}')
            for contents in node.body:
                self.visit(contents)
        self.record_instruction(f'NOP1', label=f'end_{loop_id}')

    ####
    # Not handling function calls
    ####

    def visit_FunctionDef(self, node):
        """We do not visit function definitions, they are not top level"""
        self.funcDef.append((node.name, node))
        self.funcNames.append(node.name)

    ####
    # Helper functions to
    ####

    def record_instruction(self, instruction, label=None):
        self.instructions.append((label, instruction))

    def access_memory(self, node, instruction, label=None):
        if isinstance(node, ast.Constant):
            self.record_instruction(f'{instruction} {node.value},i', label)
        else:
            temp = self.rename(node.id)

            if temp[0] == "_" and temp[1:].isupper():
                self.record_instruction(
                    f'{instruction} {temp},i', label)
            else:
                self.record_instruction(
                    f'{instruction} {temp},s', label)

    def identify(self):
        result = self.elem_id
        self.elem_id = self.elem_id + 1
        return result

    def conditons(self):
        inverted = {
            ast.Lt:  'BRGE',  # '<'  in the code means we branch if '>='
            ast.LtE: 'BRGT',  # '<=' in the code means we branch if '>'
            ast.Gt:  'BRLE',  # '>'  in the code means we branch if '<='
            ast.GtE: 'BRLT',  # '>=' in the code means we branch if '<'
            ast.NotEq: 'BREQ',  # '!=' in the code means we branch if '=='
            ast.Eq: 'BRNE',  # '==; in the code means we branch if '!='
        }
        return inverted

    def rename(self, name):
        if (name in self.vars):
            return self.vars.get(name)
        else:
            return name
