#!/usr/bin/env python
# -*- coding:utf-8 -*-
from flask import Blueprint
from flask import render_template
from flask import request, jsonify
import datetime
from datetime import timezone
from ..models import User, TokenBlocklist
from flask_jwt_extended import create_access_token,jwt_required,get_jwt
from rlhf_annotation import app,db


account = Blueprint('account', __name__)


@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username", None)
    password = request.form.get("password", None)
    # print(username,password)
    user = User.query.filter_by(username=username).one_or_none()
    if not user or not user.check_password(password):
        return jsonify("Wrong username or password"), 401

    # Notice that we are passing in the actual sqlalchemy user object here
    additional_claims = {"username": user.username, 'is_admin': user.is_admin}
    access_token = create_access_token(user, additional_claims=additional_claims)
    # access_token = create_access_token(identity=user)
    return jsonify(access_token=access_token,username=username)

# Endpoint for revoking the current users access token. Saved the unique
# identifier (jti) for the JWT into our database.
@app.route("/logout", methods=["DELETE"])
@jwt_required()
def modify_token():
    jti = get_jwt()["jti"]
    now = datetime.datetime.now()
    db.session.add(TokenBlocklist(jti=jti, created_at=now))
    db.session.commit()
    return jsonify(msg="JWT revoked")


# 获取用户名
@app.route("/get_username",methods=['GET'])
@jwt_required()
def get_username():
    jwt_data = get_jwt()
    return jsonify({'username':jwt_data['username']})





