import hashlib

m = hashlib.md5()
m.update("-L33sErq3hEy2gjrz2A_1")
x = m.hexdigest()
print x
