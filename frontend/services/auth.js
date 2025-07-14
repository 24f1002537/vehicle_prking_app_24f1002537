import axiosClient from "./axios";



export function checkUser(formdata) {
    axiosClient.get('/api/auth/login?email='+formdata.email)
    .then(resp => {
      this.$store.commit('setUser',{email:formdata.email})
      if (resp.data.found) {
        this.$router.push({name:'login',query:{found:true}})
      } else {
        this.$router.push({name:'register',query:{found:false}})
      }
    }).catch(err => { console.log(err) })
}
