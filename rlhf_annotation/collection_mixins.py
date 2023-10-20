# 实现各种容器的操作实现
from sqlitedict import SqliteDict
from persistqueue import FIFOSQLiteQueue
import tqdm


class SqliteDictMixin:
  @staticmethod
  def insert(db_path,items):
    with SqliteDict(db_path,autocommit=True) as db:
      for k,v in tqdm.tqdm(items,total=len(items)):
        db[k] = v

  @staticmethod
  def get(db_path,key):
    with SqliteDict(db_path) as db:
      try:
        return db[key]
      except KeyError:
        return None
    
  
  @staticmethod
  def delete(db_path,key,):
    with SqliteDict(db_path,autocommit=True) as db:
      del db[key]
      
  
  @staticmethod
  def get_size(db_path):
    with SqliteDict(db_path) as db:
      return len(db)
  @staticmethod
  def all_items(db_path):
    with SqliteDict(db_path) as db:
      return list(db.items())
  
class FIFOSQLiteQueueMixin:
  @staticmethod
  def insert(db_path,items):
    q = FIFOSQLiteQueue(path=db_path)
    for item in tqdm.tqdm(items,total=len(items)):
      q.put(item)
    
    del q
    
  @staticmethod
  def get(db_path, block=True, timeout=None,default=None):
    q = FIFOSQLiteQueue(path=db_path)
    if q.empty():
      return default
    item = q.get(block=block,timeout=timeout)
    del q
    return item
  
  @staticmethod
  def get_size(db_path):
    q = FIFOSQLiteQueue(path=db_path)
    ret = q.qsize()
    del q 
    return ret 
  
  @staticmethod
  def empty(db_path):
    q = FIFOSQLiteQueue(path=db_path)
    return q.empty()





    

    




        

    