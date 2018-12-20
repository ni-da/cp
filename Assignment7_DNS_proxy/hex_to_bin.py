input = 'ABC123EFFF'
for index, value in enumerate(input):
    print(value)
    print(bin(int(value, 16) + 16)[3:])

string = ''.join([bin(int(x, 16) + 16)[3:] for y, x in enumerate(input)])
print(string)
