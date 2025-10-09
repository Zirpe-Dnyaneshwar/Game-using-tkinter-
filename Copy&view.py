import numpy as np
lst=np.array([1,2,3,4])
lst1=lst.copy()
lst[0]=10
print(lst)          #[10 2 3 4]
print(lst1)         #[1 2 3 4]

# import numpy as np
# lst=np.array([1,2,3,4])
# lst1=lst.view()
# lst[0]=10
# print(lst)     #[10  2  3  4]     
# print(lst1)    #[10  2  3  4]