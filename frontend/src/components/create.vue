<template>
  <div class="add-parking-lot">
    <h2>New Parking Lot</h2>
    <el-form :model="form" ref="formRef" label-width="140px">
      <el-form-item label="Prime Location Name">
        <el-input v-model="form.locationName" />
      </el-form-item>
      <el-form-item label="Address">
        <el-input type="textarea" v-model="form.address" />
      </el-form-item>
      <el-form-item label="Pin Code">
        <el-input v-model="form.pinCode" />
      </el-form-item>
      <el-form-item label="Price (per hour)">
        <el-input v-model.number="form.price" type="number" />
      </el-form-item>
      <el-form-item label="Maximum Spots">
        <el-input v-model.number="form.maxSpots" type="number" />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="submitForm">Add</el-button>
        <el-button @click="resetForm">Home</el-button>
      </el-form-item>
    </el-form>
<div class="error" v-if="error">{{ error }}</div>
  </div>
  
</template>

<script>

export default {
    name: "CreateEntry",
  data() {
    return {
      error: '',
      form: {
        locationName: '',
        address: '',
        pinCode: '',
        price: null,
        maxSpots: null
      }
    }
  },
  methods: {
    
    async submitForm() {
      this.error = ''
      if (!this.form.locationName || !this.form.address || !this.form.pinCode || !this.form.price || !this.form.maxSpots) {
        this.error = 'All fields are required';
        return
      }
      try {
        const token = localStorage.getItem('access_token');
        if(token) {
          console.log("Token found:", token);
        }
        const response = await fetch('http://localhost:5000/create', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + token
          },
          body: JSON.stringify({
            locationName: this.form.locationName,
            address: this.form.address,
            pinCode: this.form.pinCode,
            price: this.form.price,
            maxSpots: this.form.maxSpots
          })
        })
        const data = await response.json()
        if (response.ok) {
          this.error = ''
          alert('Entry added successfully.')
          try {
        const res = await fetch("http://localhost:5000/submit-pincode", {
          method: "POST",
          headers: { "Content-Type": "application/json",
            'Authorization': 'Bearer ' + token
           },
          body: JSON.stringify({ pinCode: this.form.pinCode })
        });

        const result = await res.json();
        alert(result.message);
      } catch (err) {
        console.error(err);
        alert("Something went wrong.");
      }
          this.$router.push('/admin')
        } else {
          this.error = data.error || 'Registration failed.'
        }
      } catch (err) {
        this.error = 'Server error. Please try again later.'
      }
      
      
    },
    resetForm() {
      this.$router.push('/admin')
    }
  }
}
</script>

<style scoped>
.add-parking-lot {
  padding: 24px;
  background: #f9f9f9;
  border-radius: 8px;
}
.error {
  margin-top: 1rem;
  color: #d32f2f;
  font-weight: bold;
}
</style>
