<template>
  <div class="release-card">
    <form @submit.prevent>
      <h2>Release the parking Spot</h2>

      <label>Spot ID:</label>
      <input v-model="form.Spot_ID" readonly />

      <label>Vehicle Number:</label>
      <input v-model="form.Vehicle_Number" readonly />

      <label>Parking time:</label>
      <input v-model="form.Parking_time" readonly />

      <label>Releasing time:</label>
      <input v-model="form.Releasing_time" readonly />

      <label>Total cost:</label>
      <input v-model="form.Total_cost" readonly />

      <div class="actions">
        <button type="button" @click="releaseParkingSpot">Release</button>
        <button type="button" @click="cancel">Cancel</button>
      </div>
    </form>
  </div>
</template>

<script>
export default {
    name: "UserRelease",
  data() {
    return {
      form: {
        Spot_ID: "",
        Vehicle_Number: "",
        Parking_time: "",
        Releasing_time: "",
        Total_cost: "",
        email: ""
      }
    };
  },
  created() {
    const token = localStorage.getItem('access_token');
    const spotId = this.$route.query.spotId;
    fetch(`http://localhost:5000/api/user/occupied-spots/${spotId}`, {
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
        if (data.error) {
          console.error("Error:", data.error);
          return;
        }
        this.form.Spot_ID = spotId;
        this.form.Vehicle_Number = data.vehicle_number;
        this.form.Parking_time = data.occupied_time;
        this.form.Releasing_time = data.release_time || "Not yet released";
        this.form.Total_cost = data.cost ? `${data.cost.toFixed(2)} ` : "Not available";
        this.form.email = data.email;
      })
      .catch(error => {
        console.error("Fetch error:", error);
      });
  },
  methods: {
    async releaseParkingSpot() {
      /* TODO: call backend to release */
      const token = localStorage.getItem('access_token');
      const spotId = this.form.Spot_ID;

      try {
        const response = await fetch(`http://localhost:5000/api/user/occupied-spots/${spotId}`, {
          method: 'POST',
          headers: {
            'Authorization': 'Bearer ' + token,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            vehicle_number: this.form.Vehicle_Number,
            parking_time: this.form.Parking_time,
            releasing_time: this.form.Releasing_time,
            total_cost: this.form.Total_cost
          })
        });

        if (!response.ok) {
          throw new Error("Failed to release parking spot.");
        }

        const data = await response.json();
        if (data){
            alert('parking spot released successfully');
            this.$router.push({ path :'/user', query:{ email: data.username}})
        }
      } catch (error) {
        console.error("Error releasing parking spot:", error);
      }
    },
    cancel() {
      /* TODO: navigate back or close */
      this.$router.push({ path: '/user', query: { email: this.form.email } });
    }
  }
};
</script>

<style scoped>
.release-card {
  max-width: 420px;
  margin: 40px auto;
  padding: 24px;
  border: 1px solid #ccc;
  border-radius: 8px;
  background: #fafafa;
}
label {
  display: block;
  margin-top: 12px;
  font-weight: 600;
}
input {
  width: 100%;
  padding: 6px 8px;
  margin-top: 4px;
}
.actions {
  margin-top: 24px;
  display: flex;
  gap: 12px;
}
button {
  flex: 1;
  padding: 8px 0;
}
</style>