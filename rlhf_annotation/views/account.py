#!/usr/bin/env python
# -*- coding:utf-8 -*-
from flask import Blueprint
from flask import render_template
from flask import request, jsonify
import datetime
from datetime import timezone
from ..models import User, TokenBlocklist
from flask_jwt_extended import create_access_token,jwt_required,get_jwt,get_jwt_identity
from rlhf_annotation import app,db
from rlhf_annotation.exceptions import APIException


account = Blueprint('account', __name__)

@app.route("/login", methods=["POST"])
def login():
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





