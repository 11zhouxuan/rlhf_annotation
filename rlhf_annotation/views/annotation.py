#!/usr/bin/env python
# -*- coding:utf-8 -*-
import os
import math,json
from functools import wraps

from flask import Blueprint, request,jsonify
from flask import render_template


from werkzeug.utils import secure_filename
from rlhf_annotation import db 
from rlhf_annotation.utils import generate_random_str
import config 
from flask_jwt_extended import jwt_required,current_user,get_jwt
from flask_jwt_extended.view_decorators import verify_jwt_in_request
from flask_jwt_extended.exceptions import NoAuthorizationError
from rlhf_annotation.annotation_mixins import \
    ComparisonAnnotationTaskBuilder,QueryComparisonTaskSample

from rlhf_annotation import annotation_mixins

from rlhf_annotation.collection_mixins import \
    FIFOSQLiteQueueMixin, SqliteDictMixin
from ..models import AnnotationTask

from .admin import jwt_and_admin_required


# 任务类型到采样函数的映射
task_sample_map = {
   'comparison_annotation': QueryComparisonTaskSample
}

annotation = Blueprint('annotation', __name__)



#################################
#      实现各类标注任务视图         #
#################################
# 对比任务标注
@annotation.route('/comparison_annotation', methods=['GET'])
def comparison_annotation():
  # task_uuid = request.args['task_uuid']
  
  return render_template('comparison_annotation.html')

# sft任务标注
@annotation.route('/demonstration_annotation', methods=['GET'])
def index():
  return render_template('demonstration_annotation.html')


#################################
#         标注过程视图           #
#################################

# 获取任务样本
@annotation.route('/get_task_sample',methods=['POST'])
@jwt_required()
def get_task_sample():
  """获取标注的某些列"""
  task_uuid = request.form['task_uuid']
  sample_index =  request.form.get('sample_index',None)
  obj = AnnotationTask.query.filter_by(uuid=task_uuid).one_or_none()
  task_type = obj.task_type
  if obj is None:
     return jsonify(f'task: {task_uuid} not exist')
  
  elif obj.task_status == 'close':
     return jsonify(f'task: {task_uuid} si closed')
  
  # 获取队列中的数据
  jwt_data = get_jwt()
  username = jwt_data['username']

  # 获取下一个样本，如果没有样本则会返回None
  sample_dict = task_sample_map[task_type]().get_next_sample(obj,username,sample_index=sample_index)
  db.session.add(obj)
  db.session.commit()
  return jsonify(sample_dict)

# 提交生成结果
@annotation.route('/submit_annotated_sample',methods=['POST'])
@jwt_required()
def submit_annotated_sample():
  """提交某一行的标注"""
  task_uuid = request.form['task_uuid']
  
  obj = AnnotationTask.query.filter_by(uuid=task_uuid).one_or_none()
  if obj is  None:
     raise Exception(f'task: {task_uuid} is not found')
  
  sample = json.loads(request.form['sample'])
  annotation_mixins.SubmitComparisonTaskSample().submit_one_sample(
     obj,sample
  )

  db.session.add(obj)
  db.session.commit()
  return jsonify(code=1,msg='save success')

#################################
#        标注任务的增删查          #
#################################
# 标注任务创建相关
@annotation.route('/submit_comparison_annotation_task', methods=['POST'])
@jwt_and_admin_required()
def submit_comparison_annotation_task():
  username = current_user.username
  # 只有admin权限才能进行任务上传
  
  task_uuid = generate_random_str(config.TASK_UUID_LEN)
  annotation_work_path = os.path.join(config.DATA_WORK_PATH,task_uuid)
  # os.mkdir(annotation_work_path)
  # 文件接受
  file = request.files['file']
  filename = secure_filename(file.filename)
  
  file_folder = os.path.join(annotation_work_path,config.RAW_DATA_FOLDER_NAME)
  os.makedirs(file_folder,exist_ok=True)  # 文件夹创建
  raw_data_path = os.path.join(file_folder,filename)
  file.save(raw_data_path)
  # 任务创建
  obj = ComparisonAnnotationTaskBuilder(
    annotation_work_path
  )
  task_info = obj.create_task(raw_data_path)

  # 创建写入结果
  username = current_user.username
  task_info = dict(
    uuid = task_uuid,
    create_user = username,
    raw_data_path = raw_data_path,
    task_work_path = annotation_work_path,
    total_sample_num = task_info['total_sample_num'],
    task_queue_sample_num = task_info['total_sample_num'],
    annotated_sample_num = 0,
    in_progress_sample_num = 0,
    task_queue_path = task_info['task_queue_file_path'],
    in_progress_path = task_info['in_progress_task_file_path'],
    all_samples_path = task_info['all_sample_file_path'],
    task_type='comparison_annotation',
    task_status='created',

  )

  task_obj = AnnotationTask(
    **task_info
  )
  db.session.add(task_obj)
  db.session.commit()

  return jsonify(task_info)


# 标注任务查询
@annotation.route('/query_annotation_task', methods=['POST'])
@jwt_and_admin_required()
def query_annotation_task():
  page = int(request.form.get('page',1))
  per_page = int(request.form.get('per_page',10))
  
  tasks = AnnotationTask.query.paginate(page=page,per_page=per_page)
  # 总量
  total_task_num = db.session.query(
    AnnotationTask
  ).count()
  
  total_page_num = math.ceil(total_task_num / len(tasks))
  
  return jsonify({
    'page': page,
    'per_page': per_page,
    'total_page_num': total_page_num,
    'total_task_num': total_task_num,
    'data':[t.to_dict() for t in tasks]
  })


# 查询标注任务的进度
@annotation.route('/query_annotation_task_progress', methods=['POST'])
@jwt_required()
def query_annotation_task_progress():
   task_uuid = request.form['task_uuid']
   obj = AnnotationTask.query.filter_by(uuid=task_uuid).one_or_none()
   if obj is None:
    return jsonify({
      'msg': f'task: {task_uuid} not exist',
      'code': 1
      })
   
   return jsonify(obj.to_dict())

 

@annotation.route('/close_task', methods = ['POST'])
@jwt_and_admin_required()
def delete_annotation_task():
  task_uuid = request.args['task_uuid']
  obj = AnnotationTask.query.filter_by(uuid=task_uuid).one_or_none()
  if obj is None:
    return jsonify({
      'msg': f'task: {task_uuid} not exist',
      'code': 1
      })
  
  obj.task_status = 'close'
  obj.save()

  return jsonify({
     'code': 0,
    'msg': f'task: {task_uuid} has been closed'
  })


@annotation.route('/download_annotation_result',methods=['POST'])
@jwt_required()
def download_annotation():
   """
   下载标注结果
   """
   task_uuid = request.args['task_uuid']
   obj = AnnotationTask.query.filter_by(uuid=task_uuid).one_or_none()
   if obj is None:
    return jsonify({
      'msg': f'task: {task_uuid} not exist',
      'code': 1
      })
   
   all_samples_path = obj.all_samples_path
   all_samples = SqliteDictMixin.all_items(all_samples_path)
   
   all_samples.sort(key=lambda x: x['sample_index'])
   
  #  TODO 返回文件





   
















