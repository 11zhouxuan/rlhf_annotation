#!/usr/bin/env python
# -*- coding:utf-8 -*-

import json 

from flask import Flask,make_response
from flask import jsonify
import traceback
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from flask_jwt_extended import JWTManager
from config import JWT_ACCESS_TOKEN_EXPIRES, MAIN_DB_NAME, JWT_SECRET_KEY
from werkzeug.exceptions import HTTPException

app = Flask(__name__,template_folder='templates',static_folder='static',static_url_path='/static')

app.config["JWT_SECRET_KEY"] = JWT_SECRET_KEY  # Change this!
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{MAIN_DB_NAME}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = JWT_ACCESS_TOKEN_EXPIRES

jwt = JWTManager(app)
db = SQLAlchemy(app)


# 绑定app和数据库
migrate = Migrate(app, db)



# code = 1 表示 发生错误
# 统一异常处理
@app.errorhandler(Exception)
def handle_exception(e):
    """Return JSON instead of HTML for HTTP errors."""
    # start with the correct headers and status code from the error
    if isinstance(e, HTTPException):
        return e

    return jsonify(
        {
        "code": 1,
        'msg': str(e),
        'detail_msg': traceback.format_exc()
        }
    )



from .views.account import account
from .views.annotation import annotation
from .views.admin import admin

app.register_blueprint(account)  # 负责登录，用户管理
app.register_blueprint(annotation)  # 负责标注相关
# app.register_blueprint(admin) # 后台相关系统
 
