class FunctionEntry():

    def __init__(self, instructions, name) -> None:
        self.__instructions = instructions
        self.name = name

    def generate(self):
        print('; Function', self.name)
        for label, instr in self.__instructions:
            s = f'\t\t{instr}' if label == None else f'{str(label+":"):<9}\t{instr}'
            print(s)