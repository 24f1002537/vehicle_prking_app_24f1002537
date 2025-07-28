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
    <div class="admin-chart">
  <div style="flex:1; min-width:320px; background:#fff; border-radius:8px; margin:12px; padding:16px;">
    <h2>User Detail Distribution (Pie Chart)</h2>
    <pie-chart :chart-data="userChartData" :options="pieOptions" :key="JSON.stringify(userChartData)" />
  </div>
  <div style="flex:1; min-width:320px; background:#fff; border-radius:8px; margin:12px; padding:16px;">
    <h2>Spot Detail Distribution (Bar Chart)</h2>
    <bar-chart :chart-data="spotChartData" :options="barOptions" :key="JSON.stringify(spotChartData)" />
  </div>
</div>
      <!-- Main router view -->
      <router-view />
    </div>
     
  
</template>


<script>
import { Pie, Bar } from 'vue-chartjs';

const makeUserChartData = (user_detail) => ({
  labels: Object.keys(user_detail).map(id => `User ${id}`),
  datasets: [
    {
      backgroundColor: ['#42b983', '#ffa726', '#f44336', '#7e57c2', '#26c6da'],
      data: Object.values(user_detail)
    }
  ]
});

const makeSpotChartData = (spot_detail) => ({
  labels: Object.keys(spot_detail).map(id => `Spot ${id}`),
  datasets: [
    {
      label: 'Spot Detail',
      backgroundColor: '#ffa726',
      data: Object.values(spot_detail)
    }
  ]
});
export default {
  components: {
    'pie-chart': {
      extends: Pie,
      props: ['chartData', 'options'],
      mounted() {
        this.renderChart(this.chartData, this.options);
      }
    },
    'bar-chart': {
      extends: Bar,
      props: ['chartData', 'options'],
      mounted() {
        this.renderChart(this.chartData, this.options);
      }
    }
  },
  data() {
    return {
      isSidebarOpen: true,
      summaryObj: {
        user_detail: {  },
        spot_detail: {  }
      },
       pieOptions: {
        responsive: true,
        legend: { position: 'bottom' }
      },
      barOptions: {
        responsive: true,
        scales: {
          yAxes: [{ ticks: { beginAtZero: true, max: 1 } }]
        }
      }
    }
  },
  computed: {
    sidebarWidth() {
      return this.isSidebarOpen ? 280 : 80;
    },
    activeMenu() {
      return this.$route.path;
    },
    userChartData() {
      return makeUserChartData(this.summaryObj.user_detail);
    },
    spotChartData() {
      return makeSpotChartData(this.summaryObj.spot_detail);
    }
  },
  mounted() {
  this.fetchSummary();
},
  methods: {
    toggleSidebar() {
      this.isSidebarOpen = !this.isSidebarOpen;
    },
    logout() {
      localStorage.removeItem('access_token');
      this.$router.push('/');
    },
    async fetchSummary() {
    const token = localStorage.getItem('access_token');
    try {
      const response = await fetch('http://localhost:5000/api/admin/summary', {
        headers: {
          'Authorization': 'Bearer ' + token
        }
      });
      if (!response.ok) throw new Error('Failed to fetch summary');
      const data = await response.json();
      // Adjust this mapping if your backend returns different keys
      this.$set(this.summaryObj, 'user_detail', data.user_detail);
      this.$set(this.summaryObj, 'spot_detail', data.spot_detail);
    } catch (err) {
      console.error("Summary fetch error:", err);
    }
  }
  }

}
</script>

<style scoped>
.admin-chart {
  display: flex;
  flex-wrap: wrap;
  gap: 24px;
  padding: 20px;
  background: #f5f5f5;
  border-radius: 8px;
  margin: 20px;
  justify-content: center;
}

.AdminDashboard {
  display: flex;
  height: 97vh;
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
  