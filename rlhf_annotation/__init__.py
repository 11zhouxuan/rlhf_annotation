#!/usr/bin/env python
# -*- coding:utf-8 -*-


from flask import Flask
from flask import jsonify
from flask import request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from flask_jwt_extended import JWTManager
from config import JWT_ACCESS_TOKEN_EXPIRES, MAIN_DB_NAME, JWT_SECRET_KEY

app = Flask(__name__,template_folder='templates',static_folder='statics',static_url_path='/static')

app.config["JWT_SECRET_KEY"] = JWT_SECRET_KEY  # Change this!
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{MAIN_DB_NAME}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = JWT_ACCESS_TOKEN_EXPIRES

jwt = JWTManager(app)
db = SQLAlchemy(app)

# 绑定app和数据库
migrate = Migrate(app,db)


# Register a callback function that takes whatever object is passed in as the
# identity when creating JWTs and converts it to a JSON serializable format.
@jwt.user_identity_loader
def user_identity_lookup(user):
    return user.username

# Register a callback function that loads a user from your database whenever
# a protected route is accessed. This should return any python object on a
# successful lookup, or None if the lookup failed for any reason (for example
# if the user has been deleted from the database).
from .models import User,TokenBlocklist

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

from .views.account import account
from .views.annotation import annotation

app.register_blueprint(account)  # 负责登录，用户管理
app.register_blueprint(annotation)  # 负责标注相关

