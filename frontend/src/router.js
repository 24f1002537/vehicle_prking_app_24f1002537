import Vue from 'vue'
import VueRouter from 'vue-router'
import AdminDashboard from './components/AdminDashboard.vue'
import UserDashboard from './components/user/UserDashboard.vue'
import Login from './components/Login.vue'
import create from './components/create.vue'
import ADuser from './components/ADuser.vue'
import ADsearch from './components/ADsearch.vue'
import ADsummarry from './components/ADsummarry.vue'
import ADpedit from './components/ADpedit.vue'
import edit from './components/Adminedit.vue'
import Admineditspot from './components/Admineditspot.vue'
import userbook from './components/user/Userbook.vue'
import Userrelease from './components/user/Userrelease.vue'
import usersum from './components/user/Usersum.vue'
import Useredit from './components/user/useredit.vue'

Vue.use(VueRouter)

const routes = [
  { path: '/', component: Login },
  { path: '/admin', component: AdminDashboard },
  { path: '/user', component: UserDashboard },
  { path: '/admin/editspot', component: Admineditspot },
  { path: '/admin/generatepl', component: create },
  { path: '/admin/user', component: ADuser },
  { path: '/admin/search', component: ADsearch },
  { path: '/admin/sumary', component: ADsummarry },
  { path: '/admin/edit', component: ADpedit },
  { path: '/admin/slot/edit', component: edit },
  { path: '/user/book', component: userbook },
  { path: '/user/release', component: Userrelease },
  { path: '/user/summary', component:usersum},
  { path: '/user/edit', component: Useredit }
]

const router = new VueRouter({
  mode: 'history',
  routes
})

export default router
