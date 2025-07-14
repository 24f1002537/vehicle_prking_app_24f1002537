import Vue from 'vue'
import VueRouter from 'vue-router'
import AdminDashboard from './components/AdminDashboard.vue'
import UserDashboard from './components/UserDashboard.vue'
import Login from './components/Login.vue'

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
