#Cheaking the data type of numpy array -dtype
import numpy as np
dt=np.array([1,2,3,4,5])
print(dt.dtype) 		#int64


#Cheking the datatype of numpy array -String
import numpy as np
sd=np.array(['Apple','Banana','Cherry'])
print(sd.dtype)			#<U6   that mean unicode string


# Creating array with defined Datatype 


import numpy as nu
a=np.array([1,2,3,4,5], dtype='S') 
print(a)
print(a.dtype			#[b'1' b'2' b'3' b'4' b'5']|S1