
# 实现各种标注任务分配类
import os
from .collection_mixins import SqliteDictMixin, FIFOSQLiteQueueMixin
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
      sample = eval(line)
      _outputs = sample['outputs']
      outputs = []
      for i,output in enumerate(_outputs):
        outputs.append({
         "output":output,
         "rank": None,
         "index": i,
         "helpful_score": None
        })
      sample['outputs'] = outputs
      sample['prompt_score'] = None
      ret.append(sample)

    assert ret, f'{raw_data_path} include no data'
    return ret 
  

class QueryTaskSampleBase:

  def parse_sample(self,sample):
    """解析对应的样本"""
    raise NotImplementedError

  def get_next_sample(self,task_obj,username,sample_index=None):
    """
    task_obj: task row
    username: usename
    """
    
    task_queue_path = task_obj.task_queue_path
    in_progress_path = task_obj.in_progress_path
    all_samples_path = task_obj.all_samples_path
    
    sample = None
    if sample_index is not None:
      # 此时直接索引数据
      sample = SqliteDictMixin.get(all_samples_path,sample_index)
      sample = self.parse_sample(sample)
      SqliteDictMixin.insert(in_progress_path,[(username,sample_index)])
      task_obj.in_progress_sample_num += 1
    else:
      sample_index_come_from = 'in_progress'
      # 如果用户在in_progress中, 那么直接返回正在标注的数据即可
      sample_index = SqliteDictMixin.get(in_progress_path,username)
  
      # 如果没有在in progress中就直接从任务队列中获取
      if sample_index is None:
        sample_index_come_from = 'task_queue'
        sample_index = FIFOSQLiteQueueMixin.get(task_queue_path)

      # 索引出数据
      if sample_index is not None:
        sample = SqliteDictMixin.get(all_samples_path,sample_index)
        # print(sample_index,sample,all_samples_path)
        # print(SqliteDictMixin.get_size(all_samples_path))
        sample = self.parse_sample(sample)
        # 将sample index写入到in_progress 中
        SqliteDictMixin.insert(in_progress_path,[(username,sample_index)])
        # print(SqliteDictMixin.all_items(in_progress_path))
        # print(sample)
        # print(sg)
        if sample_index_come_from == 'task_queue':
          task_obj.task_queue_sample_num -= 1
          task_obj.in_progress_sample_num += 1
      else:
        raise Exception('task queue is empty')

    return {
      'sample_index':sample_index,
      'sample': sample,
      'sample_index_come_from': sample_index_come_from
    }
  

class QueryComparisonTaskSample(QueryTaskSampleBase):
  def parse_sample(self,sample):
    """解析对应的样本"""
    return sample
  


# 提交的单个标注结果
class SubmitTaskSampleBase:

  def bofore_save_sample(self,sample):
    """解析对应的样本"""
    raise NotImplementedError

  def submit_one_sample(self,task_obj,sample):
    task_queue_path = task_obj.task_queue_path
    in_progress_path = task_obj.in_progress_path
    all_samples_path = task_obj.all_samples_path

    sample_index = sample['sample_index']
    
    # 结果写入
    SqliteDictMixin.insert(all_samples_path,[(sample_index,self.bofore_save_sample(sample))])

    #
    SqliteDictMixin.delete(in_progress_path,sample_index)

    sample_index.in_progress_sample_num -= 1 


class SubmitComparisonTaskSample(SubmitTaskSampleBase):
  def bofore_save_sample(self,sample):
    """解析对应的样本"""
    ret = {
      "sample_index": sample['sample_index'],
      "prompt": sample['prompt'],
      "outputs": [
        {
          "output":output,
          "rank": None,
          "index": index,
          "helpful_score": None,
          "labeler": None,
          "modify_time":None
        } 
        for index,output in enumerate(sample['outputs'])
      ]
    }

    return ret













    
    







  

    

    
    
















  




    
    
    


  


  

  



