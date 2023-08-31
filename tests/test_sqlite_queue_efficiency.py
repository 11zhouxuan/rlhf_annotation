# 测试sqlite队列的效率
import time

from persistqueue import FIFOSQLiteQueue

q = FIFOSQLiteQueue(path="./test", multithreading=True)

# put 
t0 = time.time()
put_num = 100000
for i in range(put_num):
  q.put(i)

# t1 = time.time()
# print(f'put {put_num}, total time: {t1-t0}s')

# read

for i in range(1000):
  q.get()

t2 = time.time()
print('read time',t2-t0)