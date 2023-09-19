
var vue_obj = new Vue({
    el: '#app',
    delimiters: ['[[',']]','{{','}}'],
    data: function() {
      return {
         need_login: true,
         login_data: {
          "username": null,
          "password": null
         },
         is_admin: false,
         user_display_name: null,
         login_token: null,
         show_annotation_tasks: false,
         }
    },
    // 初始化的函数
    created: function () {

      // 这里的代码不能需要在vue实例构建之后执行
      // let that = this
      // that.$nextTick(function(){
      //   let userinfo_res = getUserInfo()
      //   console.log(userinfo_res)
      //   that.user_display_name = userinfo_res['username']
      //   that.is_admin = userinfo_res['is_admin']
      
      
      
},
// 监听属性
watch : {
  // need_login:{
  //   deep: true,
  //   handler: function(val) {
  //     if(val){
  //       this.user_display_name = null
  //     }
      
  // }},
  
  },

methods: {
      // 登录
      submitLogin(login_data){
        let login_res = Login(login_data)
        if(login_res['code'] == 0){
          // this.need_login = false
          // this.user_display_name = login_res['username']
          // this.is_admin = login_res['is_admin']
          window.location.href = document.referrer  // 登录成功之后跳转到前面的页面
        }else{
          this.$notify.warning({
          title: '登陆失败',
          message: login_res['msg']
      });
      }},

      // 重置表单
      resetLoginFrom(login_data){
        // console.log(login_data)
        login_data.username = null 
        login_data.password = null
      },

      // 导航栏下拉框
      // handleDropdownCommand(command){
      //   if(command == 'logout'){
      //       Logout()
      //       this.need_login = true
      //       this.resetLoginFrom()
      //   }
      // }
      
    }
    
  })




  