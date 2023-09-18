# 后台相关视图
from functools import wraps

from flask import Blueprint
from flask import render_template, jsonify

from flask_jwt_extended.view_decorators import verify_jwt_in_request
from flask_jwt_extended import get_jwt

from rlhf_annotation import app,db

admin = Blueprint('admin', __name__)


def jwt_and_admin_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            # print(claims["is_admin"])
            # print(claims)
            # print(srg)
            if claims["is_admin"]:
                return fn(*args, **kwargs)
            else:
                return jsonify({'msg':"Admins only!",'code':1}), 403
        return decorator

    return wrapper


@app.route("/admin", methods=["GET"])
def index():
    return render_template('admin.html')