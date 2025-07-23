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
          <el-menu-item  @click="logout">
  <i class="el-icon-switch-button"></i>
  <span slot="title" v-if="isSidebarOpen">Logout</span>
</el-menu-item>
        </el-menu>
      </div>
    </el-aside>
    <!-- Page Main -->
    <div class="searchbox">
      <el-select
        v-model="selectedoption"
        placeholder="Select Search Type"
        style="width: 200px;"
        popper-class="custom-dropdown"
      >
        <el-option
          v-for="opt in optionSearch"
          :key="opt.value"
          :label="opt.text"
          :value="opt.value"
        />
      </el-select>

      <!-- Address search bar -->
      <el-input
        v-if="selectedoption === 'address'"
        v-model="searchValue"
        placeholder="Enter address"
        style="width: 220px; margin-left: 16px;"
        @input="filterData"
      />

      <!-- Dropdown for other options -->
      <el-select
        v-else-if="selectedoption && selectedoption !== 'address'"
        v-model="searchValue"
        placeholder="Select value"
        style="width: 220px; margin-left: 16px;"
        @change="filterData"
      >
        <el-option
          v-for="item in getDropdownOptions(selectedoption)"
          :key="item"
          :label="item"
          :value="item"
        />
      </el-select>
    

    <!-- Filtered results -->
    <div class="dashboard-main2" style="display: flex;">
      <div
        class="box"
        v-for="parking in filteredData"
        :key="parking.id"
      >
        <div>ID: {{ parking.id }}</div>
        <div>{{ parking.occupied }}/{{ parking.maxcapacity }}</div>
        <div>Address: {{ parking.address }}</div>
        <div>Price: {{ parking.price }}</div>
        <div>Pincode: {{ parking.pincode }}</div>
        <div class="actions">
          <el-button type="primary" @click="ditLot(parking.id)">Edit</el-button>
          <el-button type="danger" @click="deleteLot(parking.id)">Delete</el-button>
        </div>
        <!-- Spot details as colored buttons (like AdminDashboard) -->
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
      selectedoption: '',
      searchValue: '',
      optionSearch: [
        { value: 'address', text: 'Location' },
        { value: 'price', text: 'Price' },
        { value: 'parking_id', text: 'Parking ID' },
        { value: 'pincode', text: 'PinCode' }
      ],
      data: [],
      filteredData: []
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
      this.data = data.data;
      this.filteredData = this.data;
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
    logout() {
      localStorage.removeItem('access_token');
      this.$router.push('/');
    },
    getDropdownOptions(option) {
      // Return unique values for the selected option from data array
      if (!option || !this.data.length) return [];
      let key = option === 'parking_id' ? 'id' : option;
      return [...new Set(this.data.map(item => item[key]))];
    },
    filterData() {
      if (!this.selectedoption || !this.searchValue) {
        this.filteredData = this.data;
        return;
      }
      let key = this.selectedoption === 'parking_id' ? 'id' : this.selectedoption;
      if (this.selectedoption === 'address') {
        this.filteredData = this.data.filter(item =>
          item.address && item.address.toLowerCase().includes(this.searchValue.toLowerCase())
        );
      } else {
        this.filteredData = this.data.filter(item =>
          item[key] == this.searchValue
        );
      }
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
          this.data = this.data.filter(lot => lot.id !== lotId);
          this.filteredData = this.filteredData.filter(lot => lot.id !== lotId);
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
  }

}
</script>

<style scoped>


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

.searchbox {
  padding: 16px;
  
  border-bottom: 1px solid #fcfcfc;
  
  align-items: center;
  justify-content: center;
}

.dashboard-main2 {
  flex: 1;
  padding: 8px;
  display: flex;
  
  gap: 16px;
}

.box {
  background: #827c7c;
  padding: 16px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  flex: 1 1 calc(30% - 32px);
  min-width: 250px;
}

.actions {
  margin-top: 12px;
  display: flex;
  gap: 8px;
}



</style>
