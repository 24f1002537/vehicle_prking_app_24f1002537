<template>
  <div class="UserDashboard">
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
        <div class="welcome-text">Welcome user</div>
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
        <el-menu-item @click="goHome">
          <i class="el-icon-house"></i>
          <span slot="title" v-if="isSidebarOpen">Home</span>
        </el-menu-item>
        <el-menu-item @click="gotosumup">
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
          <el-menu-item @click="gotoedit">
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
     <div class="home">
      <div v-if="occupiedSpots.length > 0" class="divider">
        Occupied Parking Spots
        <text class="divider-text"></text>
        Occupied Parking Spots
        <text class="divider-text"></text>
        <table class="parking-table">
          <thead>
            <tr>
              <th>Spot ID</th>
              <th>Location</th>
              <th>Vehicle Number</th>
              <th>Duration</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="spot in occupiedSpots" :key="spot.spot_id">
              <td>{{ spot.spot_id }}</td>
              <td>{{ spot.address }}</td>
              <td>{{ spot.vehicle_number }}</td>
              <td v-if="spot.occupied_time && spot.release_time">
                {{ getDuration(spot.occupied_time, spot.release_time) }}
              </td>
              <td v-else>
                {{ spot.occupied_time ? 'Ongoing' : 'N/A' }}
              </td>
              <td>
                <el-button
                  v-if="spot.status === 'occupied'"
                  type="danger"
                  size="mini"
                  @click="releaseSpot(spot.spot_id)"
                >Release</el-button>
                <el-button
                  v-else
                  type="success"
                  size="mini"
                  disabled
                >Parked Out</el-button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>  
      <div 
      class="search"
      :style="{ height: occupiedSpots.length > 0 ? '50%' : '100%' }"
      >
    
        <div>
    <!-- Search Bar -->
    <input
      type="text"
      v-model="searchQuery"
      placeholder="Search by address or pincode"
      class="search-input"
    />

    <!-- Table Results -->
    <table class="results-table">
      <thead>
        <tr>
          <th>ID</th>
          <th>Address</th>
          <th>Availability</th>
          <th>Action</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="lot in filteredLots" :key="lot.id">
          <td>{{ lot.id }}</td>
          <td>{{ lot.address }}</td>
          <td>{{ lot.available }}</td>
          <td>
            <button @click="bookLot(lot)">Book</button>
          </td>
        </tr>
      </tbody>
    </table>
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
      occupiedSpots: [],
      parkingLots: [],
      searchQuery: '',
    }
  },
  created() {
    const token = localStorage.getItem('access_token');
    fetch("http://localhost:5000/api/user/occupied-spots", {
      headers: {
        'Authorization': 'Bearer ' + token
      }
    })
      .then(response => {
        if (!response.ok) {
          throw new Error("Failed to fetch occupied spots.");
        }
        return response.json();
      })
      .then(data => {
        console.log(data.data);
        this.parkingLots = data.data;
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
    },
    filteredLots() {
    const query = this.searchQuery.trim().toLowerCase();
    if (!query) return this.parkingLots;

    return this.parkingLots.filter(lot => {
      const addressMatch = lot.address?.toLowerCase().includes(query);
      const pincodeMatch = lot.pincode?.toString().includes(query);
      return addressMatch || pincodeMatch;
    });
  }
  },
  methods: {
    async fetchOccupiedSpots() {
    const token = localStorage.getItem('access_token');
    const email = this.$route.query.email;
    try {
      const response = await fetch(`http://localhost:5000/api/user/Coccupied-spots/${email}`, {
        headers: {
          'Authorization': 'Bearer ' + token
        }
      });
      if (!response.ok) throw new Error('Failed to fetch occupied spots');
      const data = await response.json();
      // Directly assign the array if backend returns {spots: [...]}
      this.occupiedSpots = data.spots;
    } catch (err) {
      console.error(err);
    }
  },
    toggleSidebar() {
      this.isSidebarOpen = !this.isSidebarOpen;
    },
    logout() {
      localStorage.removeItem('access_token');
      this.$router.push('/');
    },
    getDuration(start, end) {
      const startTime = new Date(start);
      const endTime = new Date(end);
      const diffMs = endTime - startTime;
      const diffMins = Math.floor(diffMs / 60000);
      const hours = Math.floor(diffMins / 60);
      const mins = diffMins % 60;
      return `${hours}h ${mins}m`;
    },
    goHome() {
    const email = this.$route.query.email;
    this.$router.push({ path: '/user', query: { email } });
  },
  gotosumup(){
    const email = this.$route.query.email;
    this.$router.push({ path: '/user/summary', query: { email } });
  },
  gotoedit(){
    const email = this.$route.query.email;
    this.$router.push({ path: '/user/edit', query: { email } });
  },
    releaseSpot(spotId) {
      // Implement release logic here
      this.$router.push({ path: '/user/release', query: { spotId } });
    },
    bookLot(lot) {
  const email = this.$route.query.email;
  if (!lot.spotid) {
    alert("Error: No spotid found for this lot.");
    return;
  }

  this.$router.push({
    path: '/user/book',
    query: {
      email,
      id: lot.spotid
    }
  });
}
  },
  mounted() {
    this.fetchOccupiedSpots();
  }
}
</script>

<style scoped>
.search-input {
  margin-bottom: 1em;
  padding: 0.5em 1em;
  width: 80%;
  font-size: 1.1em;
}
.results-table {
  border-collapse: collapse;
  width: 100%;
}
.results-table th, .results-table td {
  border: 1px solid #ddd;
  padding: 8px 12px;
  text-align: left;
}
.results-table th {
  background: #eef3fd;
}
.results-table tr:hover {
  background-color: #f4f4f8;
}
button {
  background: #399efd;
  color: #fff;
  border: none;
  padding: 6px 14px;
  border-radius: 5px;
  cursor: pointer;
}
button:hover {
  background: #2978c2;
}
.divider-text {
  font-size: 24px;
  color: #000000;
  text-align: center;
  margin-bottom: 20px;
}
.home {
  width: 100%;
  height: 100%;
}
.search {
  width: 100%;
  height: 50%;
  background-color: #caeffffb;
  display: flex;
  justify-content: center;
  font-size: 24px;
  color: #776060c8;
  border-top: #1a2436 1px solid;
  border-top-left-radius: 20px;
  border-top-right-radius: 20px;
}
.divider {
  height: 50%;
  background-color: #5350506a;
  width: 100%;
  border-bottom-left-radius: 20px;
  border-bottom-right-radius: 20px;
  color: #2a3d4b;
  font-size: 24px;
  text-align: center;
  justify-content: center;
  align-items: center;
  border-bottom: #1a2436 1px solid;
}
.UserDashboard {
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

.parking-table {
  height: 40%;
  width: 80%;
  border-collapse: collapse;
  margin: 0 auto;
  background: #efbbbb;
}

.parking-table th,
.parking-table td {
  border: 1px solid #181818;
  padding: 8px 12px;
  text-align: center;
}

.parking-table th {
  background: #223047;
  color: #fff;
}

.parking-table td {
  font-size: 16px;
}
</style>
