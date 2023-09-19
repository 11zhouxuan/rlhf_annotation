#!/usr/bin/env python
# -*- coding:utf-8 -*-
from flask import Blueprint,redirect,url_for
from flask import render_template
from flask import request, jsonify
import datetime
from datetime import timezone
from ..models import User, TokenBlocklist
from flask_jwt_extended import create_access_token,jwt_required,get_jwt,get_jwt_identity
from rlhf_annotation import app,db,jwt




# 认证相关钩子函数

@jwt.user_identity_loader
def user_identity_lookup(user):
    return user.username

# code=2表示登陆问题

# token 过期callback
@jwt.expired_token_loader
def my_expired_token_callback(jwt_header, jwt_payload):
    return redirect(url_for('login', login_error_msg="token is expired"),code = 302)

# 无效token callback
@jwt.invalid_token_loader
def my_invalid_token_callback(jwt_header):
    return redirect(url_for('login', login_error_msg="invalid token"))

# 没有token callback
@jwt.unauthorized_loader
def my_unauthorized_callback(jwt_header):
    return redirect(url_for('login', login_error_msg="unauthorized token")) 
    
# token 被撤销
@jwt.revoked_token_loader
def my_revoked_token_loader_callback(jwt_header, jwt_payload):
    return redirect(url_for('login', login_error_msg="token is revoked"))


# Register a callback function that loads a user from your database whenever
# a protected route is accessed. This should return any python object on a
# successful lookup, or None if the lookup failed for any reason (for example
# if the user has been deleted from the database).
from ..models import User, TokenBlocklist

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


account = Blueprint('account', __name__)

@app.route("/login", methods=["POST","GET"])
def login():
    if request.method == "POST":
        username = request.form.get("username", None)
        password = request.form.get("password", None)
        # print(username,password)
        user = User.query.filter_by(username=username).one_or_none()
        if not user or not user.check_password(password):
            raise Exception('Wrong username or password')
            # return jsonify({'code':1,'msg':"Wrong username or password"}), 401
        # print(user.is_admin)
        # Notice that we are passing in the actual sqlalchemy user object here
        additional_claims = {"username": user.username, 'is_admin': user.is_admin}
        access_token = create_access_token(user, additional_claims=additional_claims)
        # access_token = create_access_token(identity=user)
        return jsonify(code=0,access_token=access_token,username=username,is_admin=user.is_admin)
    
    return render_template("login.html")

# Endpoint for revoking the current users access token. Saved the unique
# identifier (jti) for the JWT into our database.
@app.route("/logout", methods=["POST"])
@jwt_required()
def modify_token():
    jti = get_jwt()["jti"]
    now = datetime.datetime.now()
    db.session.add(TokenBlocklist(jti=jti, created_at=now))
    db.session.commit()
    return jsonify(code=0,msg="JWT revoked")


# 获取用户名
@app.route("/get_userinfo",methods=['POST'])
@jwt_required()
def get_userinfo():
    jwt_data = get_jwt()
    ret =  {'username':jwt_data['username'],'code':0}
    ret.update(**jwt_data)
    return jsonify(ret)


@app.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    current_user = get_jwt_identity()
    new_token = create_access_token(identity=current_user)
    return jsonify({'access_token': new_token}), 200





