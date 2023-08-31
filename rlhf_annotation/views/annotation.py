#!/usr/bin/env python
# -*- coding:utf-8 -*-
import os
import math 
from functools import wraps

from flask import Blueprint, request,jsonify
from flask import render_template


from werkzeug.utils import secure_filename
from rlhf_annotation import db 
from rlhf_annotation.utils import generate_random_str
import config 
from flask_jwt_extended import jwt_required,current_user
from flask_jwt_extended.view_decorators import _decode_jwt_from_request
from flask_jwt_extended.exceptions import NoAuthorizationError
from rlhf_annotation.annotation_mixins import ComparisonAnnotationTaskBuilder
from ..models import AnnotationTask

annotation = Blueprint('annotation', __name__)



def jwt_and_admin_required(view_function):
  @wraps(view_function)
  def wrapper(*args, **kwargs):
      jwt_data = _decode_jwt_from_request(request_type='access')

      # Do your custom validation here.
      if jwt_data['is_admin']:
          authorized = True
      else:
          authorized = False

      if not authorized:
          raise NoAuthorizationError(f"user {jwt_data['username']} is not admin")

      return view_function(*args, **kwargs)

  return jwt_required(wrapper)


# 对比任务标注
@annotation.route('/comparison_annotation', methods=['GET'])
def comparison_annotation():
  task_id = request.args['id']

  return render_template('comparison_annotation.html')


# sft任务标注
@annotation.route('/demonstration_annotation', methods=['GET'])
def index():
  return render_template('demonstration_annotation.html')


# 获取任务队列
@annotation.route('/get_task_row',methods=['POST'])
@jwt_required()
def get_task_row():
  """获取标注的某些列"""
  return "get_task_row"


# 提交生成结果
@annotation.route('/submit_annotated_row',methods=['POST'])
@jwt_required()
def submit_labeled_row():
  """提交某一行的标注"""
  return 'submit_labeled_row'



# 标注任务创建相关
@annotation.route('/submit_comparison_annotation_task', method=['POST'])
@jwt_and_admin_required
def submit_comparison_annotation_task():
  
  username = current_user['username']
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
  username = current_user['username']
  task_info = dict(
    uuid = task_uuid,
    create_user = username,
    raw_data_path = raw_data_path,
    task_work_path = annotation_work_path,
    total_sample_num = task_info['total_sample_num'],
    annotated_sample_num = 0,
    in_progress_sample_num = 0,
    task_queue_path = task_info['task_queue_file_path'],
    in_progress_path = task_info['in_progress_task_file_path'],
    all_samples_path = task_info['all_sample_file_path'],
    task_type='comparison_annotation',
    task_status='created'
  )

  task_obj = AnnotationTask(
    **task_info
  )
  db.session.add(task_obj)
  db.session.commit()

  return jsonify(task_info)


# 标注任务查询
@annotation.route('/query_task', method=['GET'])
@jwt_and_admin_required
def query_task():
  page = int(request.args.get('page',1))
  per_page = int(request.args.get('per_page',10))
  
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


@annotation.route('/delete_task', method=['GET'])
@jwt_and_admin_required
def delete_task():
  task_uuid = request.args['task_uuid']
  obj = AnnotationTask.query.filter_by(uuid=task_uuid).one_or_none()
  if obj is None:
    return jsonify({
      'msg': f'task: {task_uuid} not exist',
      'code': 1
      })
  
  obj.task_status = 'deleted'
  obj.save()

  return jsonify({
    'msg': f'task: {task_uuid} has been deleted'
  })












