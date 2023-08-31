
# 实现各种标注任务分配类
import os
from collection_mixins import SqliteDictMixin, FIFOSQLiteQueueMixin
import config


class AnnotationTaskBuilderBase:
  """
  构建标注任务, 包括数据读取, 任务队列读
  """
  
  def __init__(self, annotation_work_path) -> None:
    self.annotation_work_path = annotation_work_path

  def load_samples(self, raw_data_path):
    """实现从本地加载样本, 返回一个list"""
    raise NotImplementedError

  def create_task(self,raw_data_path):
    """
    构建一个标注任务, 返回样本的标注数量
    """
    # 获取所有的样本
    samples = self.load_samples(raw_data_path)
    
    # 将样本写入到本地数据库
    all_task_db_file_path = os.path.join(
      self.annotation_work_path, 
      config.ANNOTATION_ALL_SAMPLES_NAME
      )
    sample_items = [(i,sample) for i,sample in enumerate(samples)]
    print('正在创建all_sample索引...')
    SqliteDictMixin.insert(all_task_db_file_path,sample_items)
    
    # 将index写入到任务队列中
    indexes = [i[0] for i in sample_items]
    task_queue_file_path = os.path.join(
      self.annotation_work_path, 
      config.ANNOTATION_TASK_QUEUE_NAME
      )
    print('正在创建推送队列...')
    FIFOSQLiteQueueMixin.insert(task_queue_file_path,indexes)

    ret = {
      'total_sample_num': len(samples),
      'all_sample_file_path': all_task_db_file_path,
      'task_queue_file_path': task_queue_file_path,
      'in_progress_task_file_path': os.path.join(
        self.annotation_work_path,
        config.ANNOTATION_IN_PROGRESS_TASK_NAME
        )
    }

    return ret


class ComparisonAnnotationTaskBuilder(AnnotationTaskBuilderBase):
  """
  针对rlhf中的对比数据标注任务
  """

  def load_samples(self, raw_data_path):
    ret = []
    for line in open(raw_data_path):
      ret.append(eval(line))

    assert ret, f'{raw_data_path} include no data'
    return ret 

  




    
    
    


  


  

  



