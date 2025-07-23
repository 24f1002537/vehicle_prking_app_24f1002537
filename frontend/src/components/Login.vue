<template>
  <div class="box">
    <h1>{{ message }}</h1>
    <h2 v-text="mode === 'login' ? 'Login' : 'Register'"></h2>

    <div v-if="mode === 'login'">
      <div class="field">
        <label>Email</label>
        <input v-model="login.email" type="email" />
      </div>
      <div class="field">
        <label>Password</label>
        <input v-model="login.password" type="password" />
      </div>
      <button @click="loginUser">Login</button>
      <p>
        Don’t have an account?
        <span class="toggle" @click="switchMode">Register</span>
      </p>
    </div>

    <div v-else>
      <div class="field">
        <label>Full name</label>
        <input v-model="reg.full_name" type="text" />
      </div>
      <div class="field">
        <label>Email</label>
        <input v-model="reg.email" type="email" />
      </div>
      <div class="field">
        <label>Password</label>
        <input v-model="reg.password" type="password" />
      </div>
      <div class="field">
        <label>Address</label>
        <input v-model="reg.address" />
      </div>
      <div class="field">
        <label>Pincode</label>
        <input v-model="reg.pincode" />
      </div>
      <button @click="registerUser">Register</button>
      <p>
        Already registered?
        <span class="toggle" @click="switchMode">Login</span>
      </p>
    </div>

    <div class="error" v-if="error">{{ error }}</div>
  </div>
</template>

<script>
export default {
  name: 'LoginRegister',
  data() {
    return {
      message: 'Welcome!',
      mode: 'login',
      error: '',
      login: {
        email: '',
        password: ''
      },
      reg: {
        email: '',
        password: '',
        address: '',
        pincode: '',
        full_name: ''  // Added full_name for registration
      }
    }
  },
  methods: {
    switchMode() {
      this.error = ''
      this.mode = this.mode === 'login' ? 'register' : 'login'
    },
    async loginUser() {
      this.error = ''
      if (!this.login.email || !this.login.password) {
        this.error = 'Please enter email and password.'
        return
      }
      try {
        const response = await fetch('http://localhost:5000/api/login', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            username: this.login.email,
            password: this.login.password
          })
        })
        const data = await response.json()
        if (response.ok) {
          // Store JWT access token
          if (data.access_token) {
            localStorage.setItem('access_token', data.access_token)
          }
          // Route based on role
          if (data.role === 'admin') {
            this.$router.push('/admin')
          } else if (data.role === 'user') {
            this.$router.push({ path: '/user' , query: { email: this.login.email } })
          } else {
            this.error = 'Unknown role.'
          }
        } else {
          this.error = data.error || 'Login failed.'
        }
      } catch (err) {
        this.error = 'Server error. Please try again later.'
      }
    },
    async registerUser() {
      this.error = ''
      if (
        !this.reg.email ||
        !this.reg.password ||
        !this.reg.address ||
        !this.reg.pincode ||
        !this.reg.full_name
      ) {
        this.error = 'Please fill all registration fields.'
        return
      }
      try {
        const response = await fetch('http://localhost:5000/api/register', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            username: this.reg.email,
            password: this.reg.password,
            address: this.reg.address,
            pincode: this.reg.pincode,
            full_name: this.reg.full_name
          })
        })
        const data = await response.json()
        if (response.ok) {
          this.error = ''
          alert('Registration successful! Please login.')
          this.switchMode()
        } else {
          this.error = data.error || 'Registration failed.'
        }
      } catch (err) {
        this.error = 'Server error. Please try again later.'
      }
    }
  }
}
</script>

<style scoped>
.box {
  max-width: 400px;
  margin: 2rem auto;
  padding: 2rem;
  border: 1px solid #ddd;
  border-radius: 8px;
  background: #fafafa;
}
.field {
  margin-bottom: 1rem;
}
label {
  display: block;
  font-weight: bold;
  margin-bottom: 0.25rem;
}
input {
  width: 100%;
  padding: 0.5rem;
  box-sizing: border-box;
}
button {
  padding: 0.5rem 1.5rem;
  cursor: pointer;
  margin-top: 0.5rem;
}
.toggle {
  color: #1976d2;
  cursor: pointer;
  text-decoration: underline;
  margin-left: 0.5rem;
}
.error {
  margin-top: 1rem;
  color: #d32f2f;
  font-weight: bold;
}
</style>
