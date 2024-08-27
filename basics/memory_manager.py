x = 10
y = x
print(id(x))
print(id(y))

# 4331837200
# 4331837200


z = y
print(id(z))

z = y + 1
print(z)
print(id(z))

# 4364310288
# 4364310288
# 4364310288
# 11
# 4364310320


import sys
import weakref
class Color():
    def __init__(self, r, g, b):
        self.red = r
        self.green = g
        self.blue = b

        
clr = Color(1,2,3)
print("The ref count to object clr : ", sys.getrefcount(clr))
#  The ref count to object clr :  2

clr2 = clr
print("The ref count to object clr : ", sys.getrefcount(clr))

# The ref count to object clr :  3
del clr2
print("The ref count to object clr : ", sys.getrefcount(clr))

 
# The ref count to object clr :  2

