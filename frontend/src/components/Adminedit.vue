<template>
  <div class="edit-lot-container">
    <div class="edit-lot-header">Edit Parking Lot</div>
    <form class="edit-lot-form" @submit.prevent="onUpdate">
      <div class="form-group">
        <label>Prime Location Name :</label>
        <input
          v-model="form.primeLocationName"
          type="text"
          required
          class="edit-lot-input"
        />
      </div>
      <div class="form-group">
        <label>Address :</label>
        <textarea
          v-model="form.address"
          class="edit-lot-textarea"
          rows="3"
          required
        ></textarea>
      </div>
      <div class="form-group">
        <label>Pin code :</label>
        <input
          v-model="form.pinCode"
          type="text"
          required
          class="edit-lot-input"
        />
      </div>
      <div class="form-group">
        <label>Price (per hour) :</label>
        <input
          v-model="form.pricePerHour"
          type="number"
          required
          class="edit-lot-input"
        />
      </div>
      <div class="form-group">
        <label>Maximum spots :</label>
        <input
          v-model="form.maxSpots"
          type="number"
          required
          class="edit-lot-input"
        />
      </div>
      <!-- Add any additional fields as required -->
      <div class="form-actions">
        <button class="update-btn" type="submit">Update</button>
        <button class="cancel-btn" type="button" @click="onCancel">
          Cancel
        </button>
      </div>
      <div v-if="error">{{ error }}</div>
    </form>
  </div>
</template>

<script>
export default {
  name: "EditLot",
  data() {
    return {
      form: {
        primeLocationName: "",
        address: "",
        pinCode: "",
        pricePerHour: "",
        maxSpots: "",
      },
    };
  },
  mounted() {
    // Get lotId from query and fetch lot data from backend
    const lotId = this.$route.query.lotId;
    if (lotId) {
      this.fetchLot(lotId);
    }
  },
  methods: {
    fetchLot(lotId) {
      const token = localStorage.getItem('access_token');
      fetch(`http://localhost:5000/api/parking-lots/${lotId}`, {
        headers: {
          'Authorization': 'Bearer ' + token
        }
      })
        .then(async res => {
          if (!res.ok) throw new Error("Failed to fetch lot details");
          const data = await res.json();
          this.form = {
            primeLocationName: data.prime_location_name,
            address: data.address,
            pinCode: data.pincode,
            pricePerHour: data.price,
            maxSpots: data.number_of_spots,
          };
        })
        .catch((error) => {
          console.error(error);
          // Handle error (show message or redirect)
        });
    },
    onUpdate() {
      const lotId = this.$route.query.lotId;
      const token = localStorage.getItem('access_token');
      fetch(`http://localhost:5000/api/parking-lots/${lotId}`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          "Authorization": "Bearer " + token
        },
        body: JSON.stringify({
          primelocationname: this.form.primeLocationName,
          address: this.form.address,
          pinCode: this.form.pinCode,
          price: this.form.pricePerHour,
          maxSpots: this.form.maxSpots,
        }),
      })
        .then(async res => {
          if (!res.ok) throw new Error("Failed to update lot");
          alert("Parking lot updated successfully!");
          this.$router.go(-1);
        })
        .catch(error => {
          console.error(error);
          alert("Error updating parking lot.");
        });
    },
    onCancel() {
      this.$router.go(-1); // Go back to previous page
    },
  },
};
</script>

<style scoped>
.edit-lot-container {
  width: 420px;
  margin: 40px auto;
  background: #fff;
  border: 2px solid #e2c171;
  border-radius: 20px;
  box-shadow: 0 2px 8px rgba(80,80,30,0.05);
  font-family: 'Segoe UI', Arial, sans-serif;
  overflow: hidden;
}
.edit-lot-header {
  background: #ffe28b;
  border-bottom: 2px solid #e2c171;
  color: #444;
  padding: 14px 0 8px 0;
  font-size: 22px;
  text-align: center;
  font-weight: 700;
}
.edit-lot-form {
  padding: 26px 24px 12px 24px;
}
.form-group {
  margin-bottom: 15px;
  display: flex;
  flex-direction: column;
}
label {
  font-size: 16px;
  color: #444;
  margin-bottom: 3px;
}
.edit-lot-input {
  height: 28px;
  border-radius: 5px;
  border: 1.5px solid #b9ad90;
  padding-left: 8px;
  background: #fffde5;
  font-size: 16px;
  color: #ca8300;
}
.edit-lot-textarea {
  border-radius: 12px;
  border: 1.5px solid #b9ad90;
  background: #fffde5;
  font-size: 16px;
  color: #b88122;
  padding: 9px;
}
.form-actions {
  display: flex;
  justify-content: space-between;
  margin-top: 13px;
}
.update-btn,
.cancel-btn {
  padding: 6px 34px;
  font-size: 17px;
  border-radius: 7px;
  border: none;
  font-weight: 600;
  cursor: pointer;
}
.update-btn {
  background: #61baff;
  color: #fff;
  box-shadow: 0 2px 4px #bddcff88;
}
.cancel-btn {
  background: #c8dafe;
  color: #2273aa;
  box-shadow: 0 2px 4px #dee7f788;
}
.form-note {
  color: #e47e65;
  margin-top: 10px;
  font-size: 14px;
  text-align: right;
}
</style>
