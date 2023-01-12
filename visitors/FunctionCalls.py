from .TopLevelProgram import TopLevelProgram
import ast


class FunctionalLevel(TopLevelProgram):
    """We supports assignments and input/print calls"""

    def __init__(self, entry_point, vars, locals, args, funcNames, lable, re=None) -> None:
        super().__init__(entry_point, vars, lable)
        self.locals = locals
        self.args = args
        self.funcNames = funcNames
        self.instructions = [(entry_point, 'SUBSP ' +
                              str(len(self.locals)*2) + ',i')]
        self.re = re

    def finalize(self):
        if not self.re:
            self.instructions.append((None, 'ADDSP ' +
                                      str(len(self.locals)*2)+',i'))
            self.instructions.append((None, 'RET'))
        return self.instructions

    def visit_Assign(self, node):
        if (isinstance(node.value, ast.Call)
                and node.value.func.id in self.funcNames):

            for i, a in enumerate(node.value.args):
                if a.id in self.locals:
                    self.record_instruction(f'LDWA {self.locals[a.id]},s')
                elif self.vars[a.id] in self.args:
                    self.record_instruction(f'LDWA {self.vars[a.id]},s')
                elif a.id in self.vars:
                    self.record_instruction(f'LDWA {self.vars[a.id]},d')
                else:
                    self.record_instruction(f'LDWA {a.id},s')
                self.record_instruction(
                    f'STWA {-1*(len(node.value.args)*2-i*2+2)},s')

            self.record_instruction(f'SUBSP {len(node.value.args)*2+2},i')

            self.record_instruction(f'CALL {node.value.func.id}')
            self.record_instruction(f'ADDSP {len(node.value.args)*2},i')
            self.record_instruction(f'LDWA 0,s')
            self.record_instruction(f'ADDSP 2,i')
            if node.targets[0].id in self.locals:
                self.record_instruction(
                    f'STWA {self.locals[node.targets[0].id]},s')
            elif node.targets[0].id in self.vars:
                self.record_instruction(
                    f'STWA {self.vars[node.targets[0].id]},d')
            else:
                self.record_instruction(
                    f'STWA {node.targets[0].id},s')

        else:
            # remembering the name of the target
            if node.targets[0].id in self.locals:
                self.current_variable = self.locals[node.targets[0].id]
            else:
                self.current_variable = node.targets[0].id

            # visiting the left part, now knowing where to store the result
            self.visit(node.value)
            if self.should_save:
                super().record_instruction(f'STWA {self.current_variable},s')
            else:
                self.should_save = True
            self.current_variable = None

    def visit_Name(self, node):
        if node.id in self.locals:
            node.id = self.locals[node.id]
        super().record_instruction(f'LDWA {node.id},s')

    def visit_Call(self, node):
        match node.func.id:
            case 'int':
                # Let's visit whatever is casted into an int
                self.visit(node.args[0])
            case 'input':
                # We are only supporting integers for now
                super().record_instruction(f'DECI {self.current_variable},s')
                self.should_save = False  # DECI already save the value in memory
            case 'print':
                # We are only supporting integers for now
                super().record_instruction(f'DECO {node.args[0].id},s')
            case _:
                if (isinstance(node, ast.Call)
                        and node.func.id in self.funcNames):

                    for i, a in enumerate(node.args):
                        if self.vars[a.id] in self.args:
                            self.record_instruction(
                                f'LDWA {self.vars[a.id]},s')
                        elif a.id in self.vars:
                            self.record_instruction(
                                f'LDWA {self.vars[a.id]},d')
                        else:
                            self.record_instruction(
                                f'LDWA {a.id},d')
                        self.record_instruction(
                            f'STWA {-1*len(node.args)*2-i*2},s')

                    if node.args:
                        self.record_instruction(f'SUBSP {len(node.args)*2},i')

                    self.record_instruction(f'CALL {node.func.id}')
                    if node.args:
                        self.record_instruction(f'ADDSP {len(node.args)*2},i')

    def access_memory(self, node, instruction, label=None):
        if isinstance(node, ast.Constant):
            self.record_instruction(f'{instruction} {node.value}, i', label)
        else:
            temp = self.rename(node.id)
            if temp in self.locals or temp in self.args:
                self.record_instruction(
                    f'{instruction} {temp}, s', label)
            elif temp[0] == "_" and temp[1:].isupper():
                self.record_instruction(
                    f'{instruction} {temp},i', label)
            else:
                self.record_instruction(
                    f'{instruction} {temp},s', label)

    def visit_Return(self, node):
        if isinstance(node.value, ast.Constant):
            self.instructions.append(
                (None, 'LDWA ' + str(node.value.value) + ',i'))
            self.instructions.append((None, 'STWA ' + str(self.re) + ',s'))
            self.instructions.append((None, 'ADDSP ' +
                                      str(len(self.locals)*2)+',i'))
            self.instructions.append((None, 'RET'))
        else:
            if node.value.id in self.locals:
                self.record_instruction(f'LDWA {self.locals[node.value.id]},s')
            elif self.vars[node.value.id] in self.args:
                self.record_instruction(
                    f'LDWA {self.vars[node.value.id]},s')
            elif node.value.id in self.vars:
                self.record_instruction(
                    f'LDWA {self.vars[node.value.id]},d')
            else:
                self.record_instruction(
                    f'LDWA {node.value.id},d')
            self.record_instruction(f'STWA {self.re},s')
            self.instructions.append((None, 'ADDSP ' +
                                      str(len(self.locals)*2)+',i'))
            self.instructions.append((None, 'RET'))
