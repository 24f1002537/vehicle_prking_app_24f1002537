import Vue from 'vue'
import VueRouter from 'vue-router'
import AdminDashboard from '../views/AdminDashboard.vue'
import UserDashboard from '../views/UserDashboard.vue'
import Login from '../views/Login.vue'

Vue.use(VueRouter)

const routes = [
  { path: '/', component: Login },
  { path: '/admin', component: AdminDashboard },
  { path: '/user', component: UserDashboard }
]

const router = new VueRouter({
  mode: 'history',
  routes
})

export default router
