import timeit
print(timeit.timeit('''xyz = (i for i in range(50000))
[print(x) for x in xyz]''', number = 50))

print(timeit.timeit('[print(i) for i in range(50000)]', number = 50))