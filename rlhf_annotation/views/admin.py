# 后台相关视图
from functools import wraps
from flask_admin import Admin,AdminIndexView
from flask_admin.contrib.sqla import ModelView

from flask import Blueprint,redirect,request,url_for
from flask import render_template, jsonify

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


class UserModelView(ModelView):

    def is_accessible(self):
        print('is_accessible')
        try:
            verify_jwt_in_request(locations=['cookie'])
            
            return True 
        except:
           
            return False
        # claims = get_jwt()
        
        # return login.current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        print('dfhgdh')
        # redirect to login page if user doesn't have access
        return redirect(url_for('login', next=request.url))



class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        try:
            verify_jwt_in_request(locations=['cookie'])
            
            return True 
        except:
           
            return False
        
    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login', next=request.url))

admin = Admin(app, name='后台管理系统', template_mode='bootstrap3',index_view=MyAdminIndexView())
admin.add_view(ModelView(AnnotationTask, db.session))
admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(TokenBlocklist, db.session))

# @app.route("/admin", methods=["GET"])
# def index():
#     return render_template('admin.html')