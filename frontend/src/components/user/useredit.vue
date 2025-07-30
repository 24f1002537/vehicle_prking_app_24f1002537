<template>
  <div class="edit-wrapper">
    <!-- Back button -->
    <div class="top-bar">
      <el-button
        type="primary"
        icon="el-icon-arrow-left"
        class="back-button"
        @click="goBack"
      >
        Back to Home
      </el-button>
    </div>

    <h2>Edit Profile</h2>

    <el-form @submit.native.prevent="updateUser" label-width="100px" class="edit-form">
      <el-form-item label="Full Name">
        <el-input v-model="user.full_name" placeholder="Enter full name"></el-input>
      </el-form-item>

      <el-form-item label="Address">
        <el-input v-model="user.address" placeholder="Enter address"></el-input>
      </el-form-item>

      <el-form-item label="Pincode">
        <el-input v-model="user.pincode" placeholder="Enter pincode" type="number"></el-input>
      </el-form-item>

      <el-form-item>
        <el-button type="success" @click="updateUser">Update</el-button>
      </el-form-item>

      <el-alert
        v-if="message"
        :title="message"
        :type="success ? 'success' : 'error'"
        show-icon
        class="message-box"
        :closable="false"
      />
    </el-form>
  </div>
</template>

<script>
export default {
  name: "EditUser",
  data() {
    return {
      user: {
        full_name: "",
        address: "",
        pincode: ""
      },
      message: "",
      success: false
    };
  },
  mounted() {
    this.fetchUser();
  },
  methods: {
    async fetchUser() {
      const email = this.$route.query.email;
      const token = localStorage.getItem("access_token");
      try {
        const res = await fetch(`http://localhost:5000/api/user/profile/${email}`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        const data = await res.json();
        if (res.ok) {
          this.user = data;
        } else {
          this.message = data.error || "Failed to load user";
        }
      } catch (err) {
        this.message = "Server error";
      }
    },
    async updateUser() {
      const email = this.$route.query.email;
      const token = localStorage.getItem("access_token");
      try {
        const res = await fetch(`http://localhost:5000/api/user/update/${email}`, {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`
          },
          body: JSON.stringify(this.user)
        });
        const data = await res.json();
        this.message = data.message || data.error;
        this.success = res.ok;
      } catch (err) {
        this.message = "Server error";
        this.success = false;
      }
    },
    goBack() {
      
      const email = this.$route.query.email;
    this.$router.push({ path: "/user", query: { email } });
    }
  }
};
</script>

<style scoped>
.edit-wrapper {
  max-width: 500px;
  margin: 40px auto;
  background: #fff;
  padding: 2rem;
  border-radius: 10px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.top-bar {
  display: flex;
  justify-content: flex-start;
  margin-bottom: 1rem;
}

.back-button {
  font-weight: 500;
}

.message-box {
  margin-top: 1rem;
}
</style>
