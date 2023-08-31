from sqlitedict import SqliteDict
import random
import time

# write
t0 = time.time()
with SqliteDict('sqlite_test.db') as db:
  for i in range(1000000):
    db[i] = i

t1 = time.time()
print(t1-t0)

# read 

