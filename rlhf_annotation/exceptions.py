from werkzeug.exceptions import HTTPException
from flask import request
import json


class APIException(HTTPException):
    """
    适合restful的exception, 返回json格式
    """
    code = 500
    msg = 'sorry, api call error'
    error_code = 1
    data = ''
    
    # 自定义需要返回的信息，在初始化完成并交给父类
    def __init__(self, msg=None, code=None, error_code=None, data=None):
        if code:
            self.code = code
        if msg:
            self.msg = msg
        if error_code:
            self.error_code = error_code
        if data:
            self.data = data
        super(APIException, self).__init__(msg, None)

    @staticmethod
    def get_url_no_parm():
        full_path = str(request.path)
        return full_path

    def get_body(self, environ=None,scope=None):
        body = dict(
            error_code=self.error_code,
            msg=self.msg,
            request=request.method + ' ' + self.get_url_no_parm(),
            data=self.data
        )

        text = json.dumps(body, sort_keys=False, ensure_ascii=False)
        return text

    def get_headers(self, environ=None,scope= None):
        return [('Content-Type', 'application/json')]





