import ast
from itertools import permutations
import string

class GlobalVariableExtraction(ast.NodeVisitor):
    """ 
        We extract all the left hand side of the global (top-level) assignments
    """

    def __init__(self) -> None:
        super().__init__()
        self.results = set()
        self.vars = dict()
        self.gen = self.get_name()

    def visit_Assign(self, node):
        if len(node.targets) != 1:
            raise ValueError("Only unary assignments are supported")

        var = node.targets[0].id
        if (var not in self.vars):
            if (len(var)> 8 or var in self.vars.values()):  #checks if the variable name is greater than 8 characters long
                while var in self.vars.values() or var in self.vars: # making sure that no other rename has the new name
                    name = self.get_next()
                    var = name
                if (var[0] == '_'): #preserves constant naming convention
                    if len(name) > 8:
                        var = var[0]+(name[:-1]).upper()
                    else:
                        var = var[0]+name.upper()
                else:
                    var = name
            self.vars[node.targets[0].id] = var
                    
            node.targets[0].id = var

            if hasattr(node.value, 'value'):
                self.results.add((node.targets[0].id, node.value.value))
            else:
                self.results.add(node.targets[0].id)

                

    def visit_While(self, node):
        if(node.test.left.id in self.vars): # ensure iterator variables are set to 1 by default
            for var in self.results: # must iterate since set of tuples and strings
                if (type(var) is tuple) and (var[0] == node.test.left.id and var[1] < 1): 
                    self.results.remove(var)
                    self.results.add((node.test.left.id, 1))

        for contents in node.body:
            self.visit(contents)

    def visit_FunctionDef(self, node):
        """We do not visit function definitions, they are not global by definition"""
        pass
    
    def get_name(self):
        i = 0  # length of new rename
        possible = []

        while i <= 8:
            for p in possible:
                yield ''.join(p)
            i += 1
            possible = permutations(string.ascii_lowercase, i)  #only permutate all the possible names of length n

    def get_next(self):
        next_name = next(self.gen)
        while (next_name in self.vars):
            next_name = next(self.gen)

        return next_name