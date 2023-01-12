
class StaticMemoryAllocation():

    def __init__(self, global_vars: dict()) -> None:
        self.__global_vars = global_vars

    def generate(self):
        print('; Allocating Global (static) memory')
        for n in self.__global_vars:
            if type(n) is tuple:
                if n[0][0] == "_" and n[0][1:].isupper():
                    print(f'{str(n[0]+":"):<9}\t.EQUATE', str(n[1]))
                else:
                    print(f'{str(n[0]+":"):<9}\t.WORD', str(n[1]))
            else:
                print(f'{str(n+":"):<9}\t.BLOCK 2')  # reserving memory
