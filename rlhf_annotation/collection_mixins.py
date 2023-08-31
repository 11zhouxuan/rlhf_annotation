# 实现各种容器的操作实现
from sqlitedict import SqliteDict
from persistqueue import FIFOSQLiteQueue
import tqdm


class SqliteDictMixin:
  @staticmethod
  def insert(db_path,items):
    with SqliteDict(db_path) as db:
      for k,v in tqdm.tqdm(items,total=len(items)):
        db[k] = v
    
  @staticmethod
  def get(db_path,key):
    with SqliteDict(db_path) as db:
      value = db[key]
    return value
  
class FIFOSQLiteQueueMixin:
  @staticmethod
  def insert(db_path,items):
    q = FIFOSQLiteQueue(path=db_path)
    for item in tqdm.tqdm(items,total=len(items)):
      q.put(item)
    
    del q
    
  @staticmethod
  def get(db_path, block=True, timeout=None):
    q = FIFOSQLiteQueue(path=db_path)
    item = q.get(block=block,timeout=timeout)
    del q
    return item


    

    




        

    