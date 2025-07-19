import Vue from 'vue'
import VueRouter from 'vue-router'
import AdminDashboard from './components/AdminDashboard.vue'
import UserDashboard from './components/UserDashboard.vue'
import Login from './components/Login.vue'
import create from './components/create.vue'
import ADuser from './components/ADuser.vue'
import ADsearch from './components/ADsearch.vue'
import ADsummarry from './components/ADsummarry.vue'
import ADpedit from './components/ADpedit.vue'

Vue.use(VueRouter)

const routes = [
  { path: '/', component: Login },
  { path: '/admin', component: AdminDashboard },
  { path: '/user', component: UserDashboard },
  { path: '/admin/generatepl', component: create },
  { path: '/admin/user', component: ADuser },
  { path: '/admin/search', component: ADsearch },
  { path: '/admin/sumary', component: ADsummarry },
  { path: '/admin/edit', component: ADpedit }
]

const router = new VueRouter({
  mode: 'history',
  routes
})

export default router
