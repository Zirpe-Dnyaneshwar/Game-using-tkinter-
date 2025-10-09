'''
Datatype in NumPy
================= 
i for integer 
b for Boolean
u for unsigned integer
f for float
c for complex float
m for time delta
M for datetime 
O for object 							
S for String 
U for Unicode String 
V Memory allocation 
'''
#Creating Array With Define Datatype: 
import numpy as np
a=np.array([1,2,3,4],dtype='S')
print(a)     # This is Output Print(a) its means concatenet of string and Integer ==> [b'1' b'2' b'3' b'4']
print(a.dtype) #|S1

#Create Arrya with 4 byte int
import numpy as np
b=np.array([1,2,3,4],dtype='i4')
print(b)  #[1 2 3 4]
print(b.dtype)   #int32
