import numpy as np
lst=np.array([[1,2,3,4,5],[6,7,8,9,10]])
lst1=lst.shape
print(lst)      #[[ 1  2  3  4  5] [ 6  7  8  9 10]]
print(lst1)     #(2, 5) this is denote by dimantion of array and value of array list


import numpy as np
lst=np.array([1,2,3,4,5],ndmin=5)
print(lst)              
print(lst.shape)        

import numpy as np
lst=np.array([1,2,3,4,5],ndmin=1)
print(lst)              
print(lst.shape)        

import numpy as np
lst=np.array([1,2,3,4,5],ndmin=2)
print(lst)              
print(lst.shape)        

import numpy as np
lst=np.array([1,2,3,4,5],ndmin=5)
print(lst)              
print(lst.shape)        


import numpy as np
lst=np.array([1,2,3,4,5,6,7,8,9,10,11,12])
print(lst)              
print(lst.reshape(4,3))     #[[ 1  2  3]
                            # [ 4  5  6]
                            # [ 7  8  9]
                            # [10 11 12]