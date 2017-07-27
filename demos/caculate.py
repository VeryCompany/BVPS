from fractions import gcd
gcd(48,36)/10.0

3.6/4.8

48.0 *9.0/16.0

48.0/12800
2.7/720


int(x=1.00001)


product = 1
list = [1, 2, 3, 4]
for num in list:
    product = product * num

product

import numpy as np

a=[[1,2,3,4],
    [3,4,5,6],
    [5,6,7,8]]

b = map(lambda x: [x[0],x[1]], a)
c=reduce(lambda x,y: np.add(x,y), b)
np.divide(c,len(b))


position_cache = {
    "uid":{
        1:{
            "groupid1":{
                "cameraID1":[],
                "cameraID2":[]
            }
        },
        2:{
            "groupid1":{
                "cameraID1":[],
                "cameraID2":[]
            }
        }
    }
}
position_cache["uid"].items()
filter(lambda x: if (x[0]>1): return x, position_cache["uid"].items())
