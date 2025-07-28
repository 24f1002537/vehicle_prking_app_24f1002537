<template>
  <div class="book-parking-spot">
    <div class="form-header">
      Book the parking spot
    </div>
    <form class="booking-form" @submit.prevent="reserveSpot">
      <div class="form-row">
        <label>Spot_ID :</label>
        <input type="text" v-model="spotId" readonly class="pre-filled" />
      </div>
      <div class="form-row">
        <label>Lot_ID :</label>
        <input type="text" v-model="lotId" readonly class="pre-filled" />
      </div>
      <div class="form-row">
        <label>User ID :</label>
        <input type="text" v-model="userId" readonly class="pre-filled" />
      </div>
      <div class="form-row">
        <label>Vehicle Number :</label>
        <input type="text" v-model="vehicleNumber" placeholder="Enter vehicle number" />
      </div>
      <!-- Additional fields as required -->
      <div class="form-actions">
        <button type="submit" class="reserve-btn">Reserve</button>
        <button type="button" class="cancel-btn" @click="cancel">Cancel</button>
      </div>
    </form>
  </div>
</template>
<script>
export default {
    name: 'UserBookForm',
  data() {
    return{
    spotId: 0,
    lotId: 0,
    userId: 0,
    vehicleNumber: 0
  }
},
  created() {
    const token = localStorage.getItem('access_token');
    const email = this.$route.query.email;
    const id = this.$route.query.id;
    fetch(`http://localhost:5000/api/user/book/${email}/${id}`, {
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
        this.spotId = data.spotid;
        this.lotId = data.lotid;
        this.userId = data.userid;
        this.vehicleNumber = data.vehiclenumber;

      })
      .catch(error => {
        console.error("Fetch error:", error);
      });
  },
  methods: {
    reserveSpot() {
      const token = localStorage.getItem('access_token');
      fetch(`http://localhost:5000/api/user/book`, {
        method: 'PUT',
        headers: {
          'Authorization': 'Bearer ' + token,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          email: this.$route.query.email,
          spotid: this.spotId,
          lotid: this.lotId,
          userid: this.userId,
          vehicle_number: this.vehicleNumber
        })
      })
        .then(response => {
          if (!response.ok) {
            throw new Error("Failed to reserve spot.");
          }
          return response.json();
        })
        .then(data => {
          alert(data.message);
            this.$router.push({path: '/user', query: { email: this.$route.query.email }});
        })
        .catch(error => {
          console.error("Fetch error:", error);
        });
    },
    cancel() {
      // Reset only input fields; keep pre-filled as is
      this.vehicleNumber = '';
      this.$router.push('/user');
      // Add more logic if needed
    }
  }
};
</script>
<style scoped>
.book-parking-spot {
  border: 2px solid #bfc5c9;
  border-radius: 16px;
  width: 360px;
  margin: 32px auto;
  background: #fff;
  box-shadow: 0 4px 22px 0 #e1deea33;
}

.form-header {
  background: #ffe99a;
  text-align: center;
  font-size: 1.3em;
  padding: 12px 0;
  font-family: 'Comic Sans MS', 'Arial', sans-serif;
  border-top-left-radius: 12px;
  border-top-right-radius: 12px;
  margin-bottom: 20px;
}

.booking-form {
  padding: 0 28px 22px 28px;
}

.form-row {
  margin-bottom: 18px;
  display: flex;
  align-items: center;
}
.form-row label {
  width: 120px;
  font-family: monospace;
}
.form-row input {
  flex: 1;
  padding: 6px 13px;
  border: 1px solid #dadada;
  border-radius: 5px;
}
.pre-filled {
  background: #fdeebb;
  color: #826320;
}
.form-actions {
  display: flex;
  justify-content: space-between;
  margin-top: 25px;
}
.reserve-btn {
  background: #7dcaf4;
  color: #21395c;
  border: none;
  padding: 7px 24px;
  border-radius: 8px;
  font-weight: bold;
  cursor: pointer;
  font-family: inherit;
}
.cancel-btn {
  background: #b3d0ef;
  color: #21395c;
  border: none;
  padding: 7px 24px;
  border-radius: 8px;
  font-weight: bold;
  cursor: pointer;
  font-family: inherit;
}
.reserve-btn:hover, .cancel-btn:hover {
  background: #3d7fd1;
  color: #fff;
}
</style>

