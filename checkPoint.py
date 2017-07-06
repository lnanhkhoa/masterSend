def foo(y):
  y[0] = y[0]**2

x = [5]
foo(x)
print x[0]