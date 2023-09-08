// 实现各个api调用
// 后端地址
var ADDRESS = "http://127.0.0.1:5000"


function getJWTHeader(){
    return {
        "Authorization": `Bearer ${localStorage.getItem('token')}`
    }
}

function setJWTToken(token){
    localStorage.setItem('token',token)

}


// post 请求统一处理
function UnifiedPOSTCall(url,postdata=null){
    let ret_data = null
    $.ajax({
            url: url,
            async: false,
            type : "POST",
            data: postdata,
            headers: getJWTHeader(),
            success: function(data){ret_data = data}
})
    return ret_data
}

// function UnifiedAPICall(fn,method='POST',data=null){
//     if(method=='POST'){

//     }
// }

function getUserInfo(){
    let url = ADDRESS + '/get_userinfo'
    return UnifiedPOSTCall(url)
}


function Login(login_data){
    let url = ADDRESS + "/login"
    let login_res = UnifiedPOSTCall(url,login_data)
    console.log(login_res)
    if(login_res['code'] == 0){
        setJWTToken(login_res['access_token'])
    }
    return login_res
}

function Logout(){
    let url = ADDRESS + "/logout"
    return UnifiedPOSTCall(url)
}