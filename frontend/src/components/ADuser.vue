<template>
  <div class="AdminDashboard">
    <!-- Sidebar -->
    <el-aside
      :style="{ width: sidebarWidth + 'px', transition: 'width 0.3s cubic-bezier(.4,0,.2,1)' }"
      class="admin-sidebar"
    >
      <button class="sidebar-toggle" @click="toggleSidebar">
        <i :class="isSidebarOpen ? 'el-icon-arrow-left' : 'el-icon-arrow-right'"></i>
      </button>
      <div class="sidebar-header" v-show="isSidebarOpen">
        <el-avatar icon="el-icon-user-solid" size="large" />
        <div class="welcome-text">Welcome Admin</div>
      </div>

      <!-- Main navigation menu -->
      <el-menu
        :default-active="activeMenu"
        class="sidebar-menu"
        router
        background-color="#2d3a4b"
        text-color="#fff"
        active-text-color="#ffd04b"
      >
        <el-menu-item index="/admin">
          <i class="el-icon-house"></i>
          <span slot="title" v-if="isSidebarOpen">Home</span>
        </el-menu-item>
        <el-menu-item index="/admin/user">
          <i class="el-icon-user"></i>
          <span slot="title" v-if="isSidebarOpen">User</span>
        </el-menu-item>
        <el-menu-item index="/admin/search">
          <i class="el-icon-search"></i>
          <span slot="title" v-if="isSidebarOpen">Search</span>
        </el-menu-item>
        <el-menu-item index="/admin/sumary">
          <i class="el-icon-data-analysis"></i>
          <span slot="title" v-if="isSidebarOpen">Summary</span>
        </el-menu-item>
      </el-menu>

      <!-- Bottom menu (separate menu instance) -->
      <div class="sidebar-bottom">
        <el-menu
          router
          background-color="#2d3a4b"
          text-color="#fff"
          active-text-color="#ffd04b"
        >
          <el-menu-item index="/admin/edit">
            <i class="el-icon-edit"></i>
            <span slot="title" v-if="isSidebarOpen">Edit Profile</span>
          </el-menu-item>
          <el-menu-item @click="logout">
  <i class="el-icon-switch-button"></i>
  <span slot="title" v-if="isSidebarOpen">Logout</span>
</el-menu-item>
        </el-menu>
      </div>
    </el-aside>
    <!-- Page Main -->
    <main class="users-section">
      <h2 class="users-title">Registered Users</h2>
      <div v-if="fetchError" class="error-message">{{ fetchError }}</div>
      
      <table v-if="!fetchError" class="user-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>E-Mail</th>
            <th>Full name</th>
            <th>Address</th>
            <th>Pin code</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="user in users" :key="user.id">
            <td>{{ user.id }}</td>
            <td>{{ user.email }}</td>
            <td>{{ user.full_name }}</td>
            <td>{{ user.address }}</td>
            <td>{{ user.pincode }}</td>
          </tr>
        </tbody>
      </table>
    </main>
      <!-- Main router view -->
      <router-view />
    </div>
     
  
</template>


<script>

export default {
  data() {
    return {
      isSidebarOpen: true,
      users: [],
      fetchError: null,
      
    }
  },
  computed: {
    sidebarWidth() {
      return this.isSidebarOpen ? 280 : 80;
    },
    activeMenu() {
      return this.$route.path;
    }
  },
  created() {
                // Fetch users immediately when the app is created.
                this.fetchUsers();
            },
  methods: {
    toggleSidebar() {
      this.isSidebarOpen = !this.isSidebarOpen;
    },
    logout() {
      localStorage.removeItem('access_token');
      this.$router.push('/');
    },
    async fetchUsers() {
                    const token = localStorage.getItem('access_token');
                    try {
                        const response = await fetch('http://127.0.0.1:5000/api/admin/users',{
        headers: {
          'Authorization': 'Bearer ' + token
        }
      });

                        if (!response.ok) {
                            throw new Error('Failed to fetch users from the server.');
                        }
                        
                        this.users = await response.json();


                    } catch (error) {
                        console.error("There was an error fetching the users:", error);
                        this.fetchError = "Could not load user data. Please ensure the backend server is running.";
                    }
                }
  }

}
</script>

<style scoped>


.AdminDashboard {
  display: flex;
  height: 97vh;
}
.main-container {
  border: 2px solid #000;
  border-radius: 1rem;
  padding: 1rem;
  margin: 2rem;
  background-color: #fff;
  font-family: sans-serif;
}

.header {
  background-color: #d1fec5; /* Light green background */
  border: 1px solid #a8e698;
  border-radius: 0.5rem;
  padding: 0.75rem 1.5rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.header-title {
  font-weight: bold;
  font-size: 1.2rem;
  color: #b33d3d; /* Reddish text color */
}

.header-nav {
  display: inline-block;
  margin-left: 1.5rem;
}

.header-nav a {
  margin: 0 0.75rem;
  color: #333;
  font-weight: 500;
  text-decoration: none;
}

.header-nav a:hover {
  text-decoration: underline;
}

.edit-profile {
  color: #0000ff; /* Blue text color */
  font-weight: 600;
  cursor: pointer;
}

.edit-profile:hover {
  text-decoration: underline;
}

.users-section {
  border: 2px solid #4299e1; /* Blue border */
  border-radius: 1rem;
  padding: 1.5rem;
  margin-left: 40px;
  margin-right: 40px;
  width: 100%;
}

.users-title {
  border: 2px solid #4299e1; /* Blue border */
  border-radius: 0.5rem;
  text-align: center;
  padding: 0.5rem;
  font-size: 1.5rem;
  font-weight: 600;
  margin-bottom: 1.5rem;
  color: #2b6cb0;
}

.user-table {
  width: 100%;
  border-collapse: collapse;
}

.user-table th, .user-table td {
  border-right: 1px solid #000; /* Vertical lines */
  padding: 0.75rem;
  text-align: left;
}

.user-table th:last-child, .user-table td:last-child {
    border-right: none; /* No line for the last cell */
}


.user-table th {
  font-weight: 600;
}

.text-center {
  text-align: center;
  padding: 1rem;
}

.error-message {
  color: #721c24;
  background-color: #f8d7da;
  border: 1px solid #f5c6cb;
  padding: 0.75rem 1.25rem;
  margin-top: 1rem;
  border-radius: 0.25rem;
  text-align: center;
}


.admin-sidebar {
  height: 100%;
  background: #2d3a4b;
  overflow: hidden;
  position: relative;
  display: flex;
  flex-direction: column;
  padding: 0;
}

  .sidebar-toggle {
    position: absolute;
    top: 12px;
    right: -18px;
    z-index: 10;
    background: #223047;
    border-radius: 50%;
    border: none;
    color: #fff;
    width: 36px;
    height: 36px;
    cursor: pointer;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    transition: background 0.2s;
  }
.sidebar-toggle:hover {
  background: #1a2436;
}

.sidebar-header {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 32px 0 16px 0;
  background: #223047;
}

.welcome-text {
  color: #fff;
  margin-top: 8px;
  font-size: 18px;
  font-weight: 600;
  letter-spacing: 1px;
}

.sidebar-menu {
  border-right: none;
  background: transparent;
  flex: 1 1 auto;
}

.sidebar-bottom {
  margin-bottom: 8px;
}

.el-menu-item {
  border-radius: 4px;
  margin: 4px 12px;
  transition: background 0.2s;
}

.el-menu-item.is-active {
  background: #223047 !important;
}

.el-menu-item .el-icon {
  font-size: 22px;
  margin-right: 10px;
  vertical-align: middle;
}
</style>
  