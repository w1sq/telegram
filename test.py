import reduce

val = reduce(lambda a, b: a+b, map(lambda t: t[0]*t[1], zip([10, 20, 30], [0.1, 0.3, 0.7])), 0.0)
print(val)