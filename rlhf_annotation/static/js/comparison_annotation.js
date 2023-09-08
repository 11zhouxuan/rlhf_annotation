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
         sample_data:{
          "sample_index": 0,
          "prompt": "怎么认定是否是正当防卫？",
          "outputs": ["正当防卫是指在遭受不法侵害时，为了保护自己或者他人的人身、财产安全而采取必要的防卫行为，以制止或者防止不法侵害的犯罪行为。要认定是否是正当防卫，需要结合具体情况进行综合判断：\n1. 防卫行为是否必要：在遭受不法侵害时，必须采取必要的防卫行为，以制止或者防止不法侵害。如果防卫行为与危害结果之间没有必要关系，就不能认定是正当防卫。\n2. 防卫行为是否过分：防卫行为是否过分，需要根据实际情况来判断。如果防卫行为是必要的，但超过了必要限度，就可能被认为是“过分”的防卫行为。\n3. 防卫行为是否针对不法侵害：在遭受不法侵害时，需要采取防卫行为，但防卫行为必须针对不法侵害者本人或者与其有关的财物、物品等进行保护，否则就不能认定是正当防卫。\n综上所述，要认定是否是正当防卫，需要综合考虑防卫行为是否必要、过度，以及是否针对不法侵害者本人或者与其有关的财物、物品等进行保护等因素。", "要认定一个人是否是正当防卫，可以按照以下步骤进行：\n\n1. 找到正当防卫的相关法律条文：首先需要找到与正当防卫相关的法律条文，包括刑法第二百三十二条、第二百三十三条、第二百三十八条、第二百四十七条、第二百五十条、第二百五十二条等。\n\n2. 确定行为与法条的关联性：根据上述法律条文，找到与所描述的行为有关的条文。例如，如果一个人用手推车撞倒了一名正在行走的人，可能会被认定为正当防卫。\n\n3. 考虑行为与法条的关系：根据上述法律条文及相关案例，确定行为是否符合正当防卫的条件，包括是否具有防卫的必要性、防卫的对象是否是法律规定的权利受侵害者、防卫的手段是否合法等。\n\n4. 确定判断结果：根据以上步骤的分析和判断，最终得出判断结果，即是否认定为正当防卫。\n\n需要注意的是，在某些情况下，即使符合正当防卫的条件，也未必能够得到正当防卫的认定。例如，当防卫的行为导致他人的人身伤害或死亡，或者对他人的人身权造成严重侵犯，都可能被认为是非法行为。因此，在运用正当防卫概念时，需要根据具体情况进行判断。\n\n当然，这并不意味着正当防卫的认定是一件容易的事情。在实践中，需要结合具体情况、证据和法律规定，综合分析判断，才能得出正确的结论。同时，对正当防卫的判断也需要追求客观公正，避免主观臆断，尊重案件事实和法律程序。\n\n需要注意的是，正当防卫适用范围有限，不能作为所有情形下都适用的法律手段。只有在以下情况下，才可能认定为正当防卫：\n\n1. 防卫行为明显超过必要限度，造成重大损害的；\n2. 防卫行为是出于避免重大损害的紧迫危险而实施的。\n\n如果缺乏上述条件，行为可能不会被认定为正当防卫。因此，在判断是否是正当防卫时，需要综合考虑各种情况，并尽可能提供证据，以支持自己的判断。\n\n总体来说，正当防卫的判断需要根据具体情况进行，需要综合分析各种情况，并尽可能提供证据，以支持自己的判断。同时，需要追求客观公正，尊重案件事实和法律程序，避免主观臆断。"],
          "rank": null,
          "prompt_score": null,
         },
         candidate_table_data: []
          
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
      let need_login_array = [1,2]
      if(need_login_array.includes(userinfo_res['code'])){
        this.need_login = true 
      }else{
        this.need_login = false
        this.user_display_name = userinfo_res['username']
        this.is_admin = userinfo_res['is_admin']
      }
      
},
// 监听属性
watch : {
  need_login:{
    deep: true,
    handler: function(val) {
      if(val){
        this.user_display_name = null
      }
      
  }},
  sample_data:{
    deep: true,
    immediate:true,
    handler: function(val){
      let new_table_data = []
      for(let i=0;i<val.outputs.length;i++){
        new_table_data.push({
          'output':val.outputs[i],
          'rank':val.outputs.length,
          'index': i
        })
      }
      this.candidate_table_data = new_table_data
    }
  }

 
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
      },
      // 导航栏下拉框
      handleDropdownCommand(command){
        if(command == 'logout'){
            Logout()
            this.need_login = true
            this.resetLoginFrom()
        }
      },


      // 候选排序发生变化
      // handleRankchange(row_data){
      //   let row_index = row_data.row_index 
      //   this.candidate_table_data[row_index].rank = row_data

      // }
      
    }
    
  })