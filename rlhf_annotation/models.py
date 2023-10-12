from . import db
from hmac import compare_digest
import datetime
from sqlalchemy import TypeDecorator
from .utils import generate_random_str
from functools import partial
import config



class LiberalBoolean(TypeDecorator):
  impl = db.Boolean
  def process_bind_param(self, value, dialect):
      if value is not None:
          value = bool(int(value))
      return value
  

class User(db.Model):
  """
  用户类
  """
  id = db.Column(db.Integer, autoincrement=True,primary_key=True)
  username = db.Column(db.Text, nullable=False, unique=True)
  password = db.Column(db.Text, nullable=False)
  is_admin = db.Column(LiberalBoolean, default=False)

  # NOTE: In a real application make sure to properly hash and salt passwords
  def check_password(self, password):
      return compare_digest(password, self.password)

class TokenBlocklist(db.Model):
  """用于保存废弃token"""
  id = db.Column(db.Integer, primary_key=True)
  jti = db.Column(db.String(36), nullable=False, index=True)
  created_at = db.Column(db.DateTime, default=datetime.datetime.now)


class AnnotationTask(db.Model): 
  """标注任务表"""
  id = db.Column(db.Integer, autoincrement=True,primary_key=True)
  uuid = db.Column(db.String(config.TASK_UUID_LEN),unique=True, default=partial(generate_random_str,config.TASK_UUID_LEN))
  create_user = db.Column(db.Text,nullable=False,index=True) # 任务创建人
  created_at = db.Column(db.DateTime, default=datetime.datetime.now)
  
  raw_data_path = db.Column(db.Text,nullable=False)  # 原始数据文件的地址
  task_work_path = db.Column(db.Text,nullable=False)
  total_sample_num = db.Column(db.Integer,nullable=False)
  task_queue_sample_num = db.Column(db.Integer) # 任务队列中的样本数量
  # 已经标注的样本数量
  annotated_sample_num = db.Column(db.Integer,nullable=False, default=0)
  # 正在标注的数量
  in_progress_sample_num = db.Column(db.Integer,nullable=False, default=0)
  
  # 任务队列地址
  task_queue_path = db.Column(db.Text,nullable=False)
  in_progress_path = db.Column(db.Text,nullable=False) 
  all_samples_path = db.Column(db.Text,nullable=False) # 记录所有的样本

  # 固定任务的类型
  task_type = db.Column(db.Enum('comparison_annotation'),nullable=False)  # 任务类型
  task_status = db.Column(db.Enum('created','closed'),nullable=False)  # 任务状态

  # 上一次的修正时间
  modified_at = db.Column(db.DateTime, default=datetime.datetime.now)

  def to_dict(self):
    d = {}
    for column in self.__table__.columns:
        d[column.name] = getattr(self, column.name)
    return d
  

  class AnnotationRecord(db.Model):
    """标注记录"""
    id = db.Column(db.Integer, autoincrement=True,primary_key=True)
    task_uuid = db.Column(db.String(config.TASK_UUID_LEN))  # 任务的uuid
    smaple_id =  db.Column(db.Integer)  # 样本的id

    start_annotation_at = db.Column(db.DateTime) # 当前记录开始的时间
    created_at = db.Column(db.DateTime, default=datetime.datetime.now)
    




   

