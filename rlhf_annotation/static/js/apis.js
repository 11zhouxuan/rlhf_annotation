// 实现各个api调用
// 后端地址

var ADDRESS = "http://127.0.0.1:5000"


// post 请求统一处理, 包括各类异常统一处理
function UnifiedPOSTCall(url, postdata=null){
    if(postdata !=null){
        postdata["no_redirect"] = "true"
    }else{
        postdata = {"no_redirect": "TRUE"}
    }
    let ret_data = null
    $.ajax({
            url: url,
            async: false,
            type : "POST",
            data: postdata,
            headers: getJWTHeader(),
            success: function(data){
                // console.log('success',data)
                ret_data = data
            }
        })

// console.log('ret_data',ret_data)
if(ret_data['code'] == 2){
    // 登陆问题
    // vue_obj.need_login = true 
    vue_obj.$notify({
        title: '身份认证错误',
        message: ret_data['msg'],
        type: 'warning'
      });
    
    window.location.href = "/login?next=" + window.location.href
    throw new Error(ret_data['msg']);
}
if(ret_data['code'] == 1){
    vue_obj.$notify({
        title: 'API调用错误',
        message: ret_data['msg'],
        type: 'error'
      });
    throw new Error(ret_data['msg']);

}
    return ret_data
}


// 用户管理方面的api
function getJWTHeader(){
    return {
        "Authorization": `Bearer ${localStorage.getItem('token')}`
    }
}

function setJWTToken(token){
    localStorage.setItem('token',token)

}

function getUserInfo(){
    let url = ADDRESS + '/get_userinfo'
    return UnifiedPOSTCall(url)
}


function Login(login_data){
    let url = ADDRESS + "/login"
    console.log('login_data',login_data)
    let login_res = UnifiedPOSTCall(url,login_data)
    console.log('login_res',login_res)
    if(login_res['code'] == 0){
        setJWTToken(login_res['access_token'])
    }
    return login_res
}

function Logout(){
    let url = ADDRESS + "/logout"
    return UnifiedPOSTCall(url)
}



// admin相关api

function queryAnnotationTask(page,per_page){
    let url = ADDRESS + "/query_annotation_task"
    return UnifiedPOSTCall(url,{
        "page": page,
        "per_page": per_page
    })

}

