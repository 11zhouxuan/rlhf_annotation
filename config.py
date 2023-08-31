from datetime import timedelta
import os


TASK_UUID_LEN = 8
RAW_DATA_FOLDER_NAME = 'raw_annotation_data'
# 主要用于web的数据库地址
MAIN_DB_NAME = 'rlhf_annotation.db'
# JWT token过期时间
JWT_ACCESS_TOKEN_EXPIRES = timedelta(seconds=60*30)
JWT_SECRET_KEY = "rlhf_annotation"


# 标注相关的配置
# 标注任务队列的名称
ANNOTATION_TASK_QUEUE_NAME = 'task_queue'
# 所有标注任务的保存名称
ANNOTATION_ALL_SAMPLES_NAME = 'all_samples'
# 正在进行
ANNOTATION_IN_PROGRESS_TASK_NAME = 'in_progress'


DATA_WORK_PATH = '.annotation_works'
