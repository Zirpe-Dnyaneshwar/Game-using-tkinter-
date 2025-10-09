# # a=[1,2,3,4,5]
# # print(a)
# # print(type(a))
# # import numpy
# # b=numpy.array(a)
# # print(b)
# # print(type(b))


# import numpy
# l=[]
# for i in range(1,5):
#     n=int(input("Enter your Array Number :"))
#     l.append(n)
# print(numpy.array(l))
# print(type(l))

# 1 - D Array
import numpy as np
a=[1,2,3,4]
n=np.array(a)
print(n)
print(np.ndim(n))

# 2 - D Array
import numpy as np
a=[[1,2,3,4]]
n=np.array(a)
print(n)
print(np.ndim(n))

# 3 - D Array
import numpy as np
a=[[[1,2,3,4]]]
n=np.array(a)
print(n)
print(np.ndim(n))