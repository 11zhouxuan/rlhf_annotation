var vue_obj = new Vue({
    el: '#app',
    delimiters: ['[[',']]'],
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
         task_uuid: null,
       
         }
    },
    // 初始化的函数
    created: function () {
    //   console.log('token: ' + localStorage.getItem('token'))
      // 如果开始的时候如果没有保存令牌则需要进行登录
      // let task_uuid = localStorage.getItem('token')
      // if (!task_uuid){
        // this.need_login = true
      // }else{
        // 检查token是否过期
        // this.task_uuid = task_uuid
        // 获取username
      let userinfo_res = getUserInfo()
      console.log(userinfo_res)
      if(userinfo_res['code'] == 2){
        this.need_login = true 
      }else{
        this.need_login = false
        this.user_display_name = userinfo_res['username']
      }
      
},
// 监听属性
watch : {
  need_login:function(val) {
          if(val){
            this.user_display_name = null
          }
          
      },
      
  },

methods: {
      // 登录
      submitLogin(login_data){
        let login_res = Login(login_data)
        if(login_res['code'] == 0){
          this.need_login = false
          this.user_display_name = login_res['username']
          this.is_admin = login_res['is_admin']
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
      }
      
    }
    
  })