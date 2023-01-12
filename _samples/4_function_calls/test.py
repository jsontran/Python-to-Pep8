def mult(x, y):
    result = 0
    while y > 0:
        result = result + x
        y = y - 1
    return result

a = 5
b = 4
val = mult(a, b)
print(val)
