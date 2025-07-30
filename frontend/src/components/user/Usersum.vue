<template>
  <div class="UserDashboard">
    <!-- Sidebar (Existing Code) -->
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
      <el-menu :default-active="activeMenu" class="sidebar-menu" router background-color="#2d3a4b" text-color="#fff" active-text-color="#ffd04b">
        <el-menu-item @click="goHome">
          <i class="el-icon-house"></i>
          <span slot="title" v-if="isSidebarOpen">Home</span>
        </el-menu-item>
        <el-menu-item @click="gotosumup">
          <i class="el-icon-data-analysis"></i>
          <span slot="title" v-if="isSidebarOpen">Summary</span>
        </el-menu-item>
      </el-menu>
      <div class="sidebar-bottom">
        <el-menu router background-color="#2d3a4b" text-color="#fff" active-text-color="#ffd04b">
          <el-menu-item @click="gotoedit">
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

    <!-- Main Content Area (Updated) -->
    <el-main class="content-area">
      <div class="summary-header">
        <h1>Revenue Summary</h1>
        <p>Your daily and monthly revenue breakdown.</p>
      </div>

      <!-- Loading and Error States -->
      <el-alert v-if="isLoading" title="Loading revenue data..." type="info" :closable="false" center show-icon></el-alert>
      <el-alert v-if="error" :title="error" type="error" :closable="false" center show-icon></el-alert>

      <!-- Main Content when data is loaded -->
      <div v-if="!isLoading && !error" class="summary-content">
        <!-- Data Filters -->
        <el-card class="filter-card" v-if="availableYears.length > 0">
          <div class="filter-controls">
            <!-- Chart Type Dropdown -->
            <el-select v-model="chartType" placeholder="Select Chart Type" style="width: 180px;">
              <el-option label="Daily Revenue" value="daily"></el-option>
              <el-option label="Monthly Revenue" value="monthly"></el-option>
            </el-select>
            <!-- Year Dropdown -->
            <el-select v-model="selectedYear" placeholder="Select Year" @change="handleYearChange">
              <el-option v-for="year in availableYears" :key="year" :label="year" :value="year"></el-option>
            </el-select>
            <!-- Month Dropdown (Only for Daily Chart) -->
            <el-select v-if="chartType === 'daily'" v-model="selectedMonth" placeholder="Select Month" :disabled="!selectedYear">
              <el-option v-for="month in availableMonths" :key="month.value" :label="month.name" :value="month.value"></el-option>
            </el-select>
          </div>
        </el-card>

        <!-- Chart Display -->
        <el-card class="chart-card" v-if="chartData">
          <!-- Daily Line Chart -->
          <line-chart v-if="chartType === 'daily'" :chart-data="chartData" :options="lineChartOptions"></line-chart>
          <!-- Monthly Bar Chart -->
          <bar-chart v-else :chart-data="chartData" :options="barChartOptions"></bar-chart>
        </el-card>

        <!-- No Data Message -->
        <el-alert v-if="!chartData && !isLoading" title="No revenue data found for the selected period." type="warning" center show-icon :closable="false"></el-alert>
      </div>
    </el-main>
    <button @click="lookupAndGenerate" class="sumbutton">summary</button>
  </div>
</template>

<script>
// Import the chart types directly from vue-chartjs
import { Line, Bar } from 'vue-chartjs';

export default {
  name: "UserSummary",
  components: {
    // Define chart components locally instead of importing files
    'line-chart': {
      extends: Line,
      props: ['chartData', 'options'],
      mounted () {
        this.renderChart(this.chartData, this.options);
      },
      // Add a watcher to re-render the chart when data changes
      watch: {
        chartData () {
          this.$data._chart.destroy();
          this.renderChart(this.chartData, this.options);
        }
      }
    },
    'bar-chart': {
      extends: Bar,
      props: ['chartData', 'options'],
      mounted () {
        this.renderChart(this.chartData, this.options);
      },
      watch: {
        chartData () {
          this.$data._chart.destroy();
          this.renderChart(this.chartData, this.options);
        }
      }
    }
  },
  data() {
    return {
      message: '',
    success: false,
      isSidebarOpen: true,
      isLoading: true,
      error: null,
      revenueData: {},
      chartType: 'daily', // 'daily' or 'monthly'
      selectedYear: null,
      selectedMonth: null,
      // Chart.js options for Line Chart
      lineChartOptions: {
        responsive: true, maintainAspectRatio: false,
        scales: {
          yAxes: [{ ticks: { beginAtZero: true, callback: (value) => `₹${value.toFixed(2)}` }, scaleLabel: { display: true, labelString: 'Revenue (INR)' } }],
          xAxes: [{ scaleLabel: { display: true, labelString: 'Day of the Month' } }]
        },
        tooltips: { callbacks: { label: (tooltipItem, data) => `${data.datasets[tooltipItem.datasetIndex].label || ''}: ₹${Number(tooltipItem.yLabel).toFixed(2)}` } }
      },
      // Chart.js options for Bar Chart
      barChartOptions: {
        responsive: true, maintainAspectRatio: false,
        legend: { display: false },
        scales: {
          yAxes: [{ ticks: { beginAtZero: true, callback: (value) => `₹${value.toFixed(2)}` }, scaleLabel: { display: true, labelString: 'Total Revenue (INR)' } }],
          xAxes: [{ scaleLabel: { display: true, labelString: 'Month' } }]
        },
        tooltips: { callbacks: { label: (tooltipItem) => `Total Revenue: ₹${Number(tooltipItem.yLabel).toFixed(2)}` } }
      }
    };
  },
  computed: {
    sidebarWidth() { return this.isSidebarOpen ? 280 : 80; },
    activeMenu() { return this.$route.path.includes('/summary') ? '/user/summary' : this.$route.path; },
    availableYears() { return Object.keys(this.revenueData).sort((a, b) => b - a); },
    availableMonths() {
      if (!this.selectedYear) return [];
      const monthNumbers = Object.keys(this.revenueData[this.selectedYear]).sort((a, b) => a - b);
      return monthNumbers.map(month => ({ value: month, name: this.getMonthName(month) }));
    },
    chartData() {
      if (this.chartType === 'daily') {
        return this.dailyChartData;
      } else {
        return this.monthlyChartData;
      }
    },
    dailyChartData() {
      if (!this.selectedYear || !this.selectedMonth || !this.revenueData[this.selectedYear]?.[this.selectedMonth]) {
        return null;
      }
      const dailyData = this.revenueData[this.selectedYear][this.selectedMonth];
      const labels = Object.keys(dailyData).sort((a, b) => a - b);
      const data = labels.map(day => dailyData[day]);
      return {
        labels: labels.map(day => `Day ${day}`),
        datasets: [{
          label: `Daily Revenue`,
          data: data,
          backgroundColor: 'rgba(75, 192, 192, 0.2)',
          borderColor: 'rgba(75, 192, 192, 1)',
          borderWidth: 2,
          pointBackgroundColor: 'rgba(75, 192, 192, 1)',
        }]
      };
    },
    monthlyChartData() {
      if (!this.selectedYear || !this.revenueData[this.selectedYear]) {
        return null;
      }
      const yearData = this.revenueData[this.selectedYear];
      const monthLabels = this.availableMonths.map(m => m.name);
      const data = this.availableMonths.map(month => {
        const monthData = yearData[month.value] || {};
        // Sum all daily revenues for the month
        return Object.values(monthData).reduce((total, revenue) => total + revenue, 0);
      });
      return {
        labels: monthLabels,
        datasets: [{
          label: `Monthly Revenue for ${this.selectedYear}`,
          data: data,
          backgroundColor: 'rgba(255, 99, 132, 0.5)',
          borderColor: 'rgba(255, 99, 132, 1)',
          borderWidth: 1,
        }]
      };
    }
  },
  methods: {
    toggleSidebar() { this.isSidebarOpen = !this.isSidebarOpen; },
    logout() { localStorage.removeItem('access_token'); this.$router.push('/'); },
    goHome() { const email = this.$route.query.email; this.$router.push({ path: '/user', query: { email } }); },
    gotosumup() { const email = this.$route.query.email; this.$router.push({ path: '/user/summary', query: { email } }); },
    gotoedit() { const email = this.$route.query.email; this.$router.push({ path: '/user/edit', query: { email } }); },
    
    async fetchRevenueData() {
      this.isLoading = true;
      this.error = null;
      const email = this.$route.query.email;

      // Get the JWT token from localStorage
      const token = localStorage.getItem('access_token');

      // Check if the token exists before making the request
      if (!token) {
        this.error = "Authentication token not found. Please log in.";
        this.isLoading = false;
        return;
      }

      if (!email) {
        this.error = "User email not found in URL. Please log in again.";
        this.isLoading = false;
        return;
      }

      try {
        // Using native fetch API and adding the Authorization header
        const response = await fetch(`http://127.0.0.1:5000/api/user/summary/${email}`, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
        
        // Handle 401 Unauthorized error specifically
        if (response.status === 401) {
            this.error = "Your session has expired. Please log out and log in again.";
            this.isLoading = false;
            // Optionally, clear the expired token
            // localStorage.removeItem('access_token');
            return;
        }

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();

        if (data.error) {
            this.error = data.error;
        } else {
            this.revenueData = data;
            if (this.availableYears.length > 0) {
              this.selectedYear = this.availableYears[0];
              if (this.availableMonths.length > 0) {
                this.selectedMonth = this.availableMonths[this.availableMonths.length - 1].value;
              }
            }
        }
      } catch (err) {
        console.error("Failed to fetch revenue data:", err);
        this.error = "Failed to connect to the server. Please try again later.";
      } finally {
        this.isLoading = false;
      }
    },
    handleYearChange() {
      if (this.chartType === 'daily') {
        if (this.availableMonths.length > 0) {
          this.selectedMonth = this.availableMonths[0].value;
        } else {
          this.selectedMonth = null;
        }
      }
    },
    getMonthName(monthNumber) {
      const date = new Date();
      date.setMonth(parseInt(monthNumber, 10) - 1);
      return date.toLocaleString('en-US', { month: 'short' }); // Using short month name
    },
    async lookupAndGenerate() {
  this.message = '';
  const token = localStorage.getItem('access_token'); // FIXED token key
  const email = this.$route.query.email;

  try {
    const userRes = await fetch(`http://localhost:5000/api/user/lookup/${email}`);
    const userData = await userRes.json();

    if (!userRes.ok || !userData.user_id) {
      throw new Error(userData.error || 'User lookup failed.');
    }

    const userId = userData.user_id;

    const reportRes = await fetch(
      `http://localhost:5000/api/user/report/${email}/${userId}`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`, // use correct token
        },
      }
    );

    const reportData = await reportRes.json();

    if (!reportRes.ok) {
      throw new Error(reportData.error || 'Failed to trigger report generation.');
    }

    this.message = reportData.message;
    this.success = true;
    this.$message({ type: 'success', message: 'Report generation triggered!' });
  } catch (err) {
    this.message = err.message;
    this.success = false;
    this.$message({ type: 'error', message: this.message });
  }
}

  },
  created() {
    this.fetchRevenueData();
  }
};

</script>

<style scoped>
/* Add global box-sizing rule */
* {
  box-sizing: border-box;
}

.sumbutton {
  position: absolute;
  
  right: 20px;
  padding: 10px 20px;
  background-color: #409eff;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-size: 16px;
}
.UserDashboard {
  display: flex;
  height: 97vh; /* Matched from UserDashboard.vue */
  background-color: #f4f7f9;
  overflow: hidden; 
}

.admin-sidebar {
  height: 100%;
  background: #2d3a4b;
  overflow: hidden;
  position: relative;
  display: flex;
  flex-direction: column;
  padding: 0;
  flex-shrink: 0;
}

.sidebar-toggle {
  position: absolute; top: 12px; right: -18px; z-index: 10; background: #223047;
  border-radius: 50%; border: none; color: #fff; width: 36px; height: 36px;
  cursor: pointer; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1); transition: background 0.2s;
}
.sidebar-toggle:hover { background: #1a2436; }

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

.content-area {
  padding: 2rem;
  display: flex;
  flex-direction: column;
  flex-grow: 1;
  overflow-y: auto;
}

.summary-content {
    display: flex;
    flex-direction: column;
    flex-grow: 1;
    min-height: 0;
}

.summary-header {
  margin-bottom: 2rem;
  flex-shrink: 0;
}

.summary-header h1 {
  font-size: 2rem;
  font-weight: 700;
  color: #1a202c;
  margin: 0;
}

.summary-header p {
  font-size: 1rem;
  color: #718096;
  margin-top: 0.5rem;
}

.filter-card {
  margin-bottom: 1.5rem;
  flex-shrink: 0;
}

.filter-controls {
  display: flex;
  gap: 1rem;
}

.chart-card {
  padding: 1.5rem;
  flex-grow: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
}
</style>
