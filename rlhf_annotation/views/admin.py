# 后台相关视图
from flask import Blueprint
from flask import render_template

from rlhf_annotation import app,db

admin = Blueprint('admin', __name__)


@app.route("/admin", methods=["POST"])
def index():
    return render_template('admin.html')