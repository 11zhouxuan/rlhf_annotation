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


# Register a callback function that takes whatever object is passed in as the
# identity when creating JWTs and converts it to a JSON serializable format.
@jwt.user_identity_loader
def user_identity_lookup(user):
    return user.username

# token 过期callback
@jwt.expired_token_loader
def my_expired_token_callback(jwt_header, jwt_payload):
    return jsonify(code=2, msg="token is expired")

# 无效token callback
@jwt.invalid_token_loader
def my_invalid_token_callback(jwt_header):
    return jsonify(code=2, msg='invalid token')

# 没有token callback
@jwt.unauthorized_loader
def my_unauthorized_callback(jwt_header):
    return jsonify(code=2, msg='unauthorized token')
    
# token 被撤销
@jwt.revoked_token_loader
def my_revoked_token_loader_callback(jwt_header, jwt_payload):
    return jsonify(code=1, msg=' token is revoked')


# Register a callback function that loads a user from your database whenever
# a protected route is accessed. This should return any python object on a
# successful lookup, or None if the lookup failed for any reason (for example
# if the user has been deleted from the database).
from .models import User, TokenBlocklist

@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    username = jwt_data["username"]
    return User.query.filter_by(username=username).one_or_none()


# 判断token是否过期
@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload: dict) -> bool:
    jti = jwt_payload["jti"]
    token = db.session.query(TokenBlocklist.id).filter_by(jti=jti).scalar()
    return token is not None

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
app.register_blueprint(admin) # 后台相关系统
 
