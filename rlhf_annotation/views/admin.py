# 后台相关视图
import traceback
from functools import wraps
from flask_admin import Admin,AdminIndexView
from flask_admin.contrib.sqla import ModelView

from flask import Blueprint,redirect,request,url_for
from flask import render_template, jsonify
from flask import request

from flask_jwt_extended.view_decorators import verify_jwt_in_request
from flask_jwt_extended import get_jwt

from rlhf_annotation import app,db

app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'



# admin = Blueprint('admin', __name__)


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


from ..models import User,AnnotationTask,TokenBlocklist
# from flask_admin.contrib.sqla import ModelView


def valid_admin():
    try:
        verify_jwt_in_request(locations=['cookies'])
        claims = get_jwt()
        # print(claims)
        if not claims["is_admin"]:
            raise Exception('need admin premission')
        return True 
    except:
        print(traceback.format_exc())
        return False
           



class MyAdminModelView(ModelView):

    def is_accessible(self):
        return valid_admin()

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login', next=request.url))

class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        return valid_admin()
        
    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login', next=request.url))

admin = Admin(app, name='后台管理系统', template_mode='bootstrap3',index_view=MyAdminIndexView())
admin.add_view(MyAdminModelView(AnnotationTask, db.session))
admin.add_view(MyAdminModelView(User, db.session))
admin.add_view(MyAdminModelView(TokenBlocklist, db.session))
