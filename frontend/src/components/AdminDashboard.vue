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
          <el-menu-item index="/logout" @click="logout">
            <i class="el-icon-switch-button"></i>
            <span slot="title" v-if="isSidebarOpen">Logout</span>
          </el-menu-item>
        </el-menu>
      </div>
    </el-aside>
    <!-- Page Main -->
    <div class="dashboard-main">
      <el-button
        type="primary"
        icon="el-icon-plus"
        class="add-btn"
        @click="goToAdd"
      >
        Add
      </el-button>
      <h1>Parking lots</h1>
      <div class="dashboard-main2" style="display: flex;">
        
      <div class="box" style="border: #1a2436 1px solid;width: 30%;margin-right: 10px;border-radius: 8px; justify-items: center;" v-for="parking in dataArray" :key="parking.id">
    <!-- Display main ID and occupied/maxcapacity -->
    <div>ID: {{ parking.id }}</div>
    <div>{{ parking.occupied }}/{{ parking.maxcapacity }}</div>
    <div class="actions">
      <el-button type="primary" @click="ditLot(parking.id)">Edit</el-button>
      <el-button type="danger" @click="deleteLot(parking.id)">Delete</el-button>
    </div>

    <div style="display: flex; flex-wrap: wrap; margin-top: 10px;">
      <el-button
        v-for="spot in parking.spotdetail"
        :key="spot.id"
        :style="getBoxStyle(spot.occupied)"
        class="spot-box"
        @click="editSpot(spot.id)"
      >
        {{ spot.occupied === 1 ? "O" : "A" }}
      </el-button>
    </div>
  </div>
      </div>
      </div>
      <!-- Main router view -->
      <router-view />
    </div>
     
  
</template>


<script>

export default {
  data() {
    return {
      isSidebarOpen: true,
      dataArray: {}
    }
  },
    created() {
  const token = localStorage.getItem('access_token');
  fetch("http://localhost:5000/admin", {
    headers: {
      'Authorization': 'Bearer ' + token
    }
  })
    .then(response => {
      if (!response.ok) {
        throw new Error("Failed to fetch parking lot data.");
      }
      return response.json();
    })
    .then(data => {
      console.log(data);
      this.dataArray = data.data;
    })
    .catch(error => {
      console.error("Fetch error:", error);
    });
},
  computed: {
    sidebarWidth() {
      return this.isSidebarOpen ? 280 : 80;
    },
    activeMenu() {
      return this.$route.path;
    }
  },
  methods: {
    toggleSidebar() {
      this.isSidebarOpen = !this.isSidebarOpen;
    },
    goToAdd() {
      this.$router.push('/admin/generatepl');
    },
    ditLot(lotId) {
      alert("Edit lot: " + lotId);
      this.$router.push({ path: '/admin/slot/edit', query: { lotId: lotId } });
    },
    deleteLot(lotId) {
      alert("Delete lot: " + lotId);
      const token = localStorage.getItem('access_token');
      fetch("http://localhost:5000/delete/lot/" + lotId, {
        method: 'DELETE',
        headers: {
          'Authorization': 'Bearer ' + token
        }
      }).then(async response => {
        const data = await response.json();
        if (response.ok) {
          this.dataArray = this.dataArray.filter(lot => lot.id !== lotId);
          alert(data.message); // "parking lot deleted"
        } else {
          throw new Error(data.error || "Unknown error");
        }
      })
      .catch(error => {
        console.error("ERROR deleting parking lot:", error.message);
        alert("Failed to delete parking lot");
      });
    },
    getBoxStyle(occupied) {
  return {
    border : '1px solid #ccc',
    width: '30px',
    height: '30px',
    background: occupied ? 'red' : 'green',
    color: 'white',
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    margin: '4px',
    borderRadius: '4px',
    fontWeight: 'bold'
  };
},
    editSpot(spotId) {
      alert("Edit spot: " + spotId);
      this.$router.push({ path: '/admin/editspot', query: { spotId: spotId } });
    },
    logout() {
      localStorage.removeItem('access_token');
      this.$router.push('/');
    }
  }
}
</script>

<style scoped>
.dashboard-main2 {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  padding: 10px;
  box-sizing: border-box;
}
.box {
  flex: 1 1 calc(30% - 14px); /* Force 3-per-row */
  border: #1a2436 1px solid;
  border-radius: 8px;
  padding: 10px;
  box-sizing: border-box;
  min-width: 250px; /* Optional */
}
.AdminDashboard {
  display: flex;
  height: 97vh;
}
.dashboard-boxes {
  display: flex;
  gap: 16px;
  margin-bottom: 32px;
  width: 100%;
}
.dashboard-box {
  background: #585656;
  border-radius: 8px;
  box-shadow: 0 2px 8px #0001;
  height: 150px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 18px;
}


.heading {
  position: absolute;
  height: 40px;
  top: 20px;
  left: 300px;
  font-size: 24px;
  font-weight: bold;
  color: #2c3e50;
}
.dashboard-main {
  flex: 1;
  padding: 24px;
  overflow: auto;
  position: relative;
}

.add-btn {
  margin-bottom: 24px;
  float: right;
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