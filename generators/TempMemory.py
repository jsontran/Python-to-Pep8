
class TempMemoryAllocation():

    def __init__(self, local, args, re, name) -> None:
        self.name = name
        self.local = local
        self.args = args
        self.re = re

    def generate(self):
        print('; Allocating Temp memory for ', self.name)
        print('; local variables')
        local_count = 1
        for n in self.local:
            print(f'{str(self.local[n]+":"):<9}\t.EQUATE', str(local_count*2-2))
            local_count += 1

        print('; parameters')
        args_count = 1
        total_local = len(self.local)
        for arg in self.args:
            print(f'{str(arg+":"):<9}\t.EQUATE', str(args_count*2+total_local*2))
            args_count += 1
        
        if self.re != False:
            print('; return')
            total_param =len(self.args)
            print(f'{str(self.re+":"):<9}\t.EQUATE', str(total_param*2+total_local*2+2))

            
