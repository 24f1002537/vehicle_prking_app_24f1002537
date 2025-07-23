<template>
  <div>
    <!-- View/Delete Parking Spot -->
    <div v-if="!showDetails" class="parking-spot-container">
      <div class="header">View/Delete Parking Spot</div>
      <div class="field-row">
        <label>ID :</label>
        <div class="value-box">{{ local.id }}</div>
      </div>
      <div class="field-row">
        <label>Status :</label>
        <button
          class="status-btn"
          :class="{'occupied': local.status === 'O', 'available': local.status === 'A'}"
          @click="local.status === 'O' && showOccupiedDetails()"
        >
          {{ local.status }}
        </button>
      </div>
      <!-- Placeholders for additional fields -->
      <div class="btn-row">
        <button
          class="delete-btn"
          :disabled="local.status !== 'A'"
          @click="deleteSpot"
        >
          Delete
        </button>
        <button class="close-btn" @click="close">Close</button>
      </div>
      <div v-if="local.status !== 'A'" class="note">
        Note: Can't delete the occupied parking spot
      </div>
    </div>

    <!-- Occupied Parking Spot Details -->
    <div v-if="showDetails" class="occupied-details-container">
      <div class="header">Occupied Parking Spot Details</div>
      <div class="field-row">
        <label>ID :</label>
        <div class="value-box">{{ local.id }}</div>
      </div>
      <div class="field-row">
        <label>Customer ID :</label>
        <div class="value-box">{{ local.customerId }}</div>
      </div>
      <div class="field-row">
        <label>Vehicle number :</label>
        <div class="value-box">{{ local.vehicleNumber }}</div>
      </div>
      <div class="field-row">
        <label>Reserved at :</label>
        <div class="value-box">{{ local.reservedAt }}</div>
      </div>
      <div class="field-row">
        <label>Released at :</label>
        <div class="value-box">{{ local.leaveAt }}</div>
      </div>
      <div class="field-row">
        <label>Est. parking cost :</label>
        <div class="value-box">{{ local.cost }}</div>
      </div>
      <div class="etc-fields">etc., fields....</div>
      <div class="btn-row">
        <button class="close-btn" @click="closeDetails">Close</button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "AdminEditSpot",
  data() {
    return {
      showDetails: false, // For displaying occupied details
      local: {
        id: "",
        status: "",
        customerId: "",
        vehicleNumber: "",
        reservedAt: "",
        leaveAt: "",
        cost: ""
      }
    };
  },
  mounted() {
    // Example fetch logic; updates only local
    const spotId = this.$route.query.spotId;
    console.log("Spot ID:", spotId);
    if (spotId) {
      this.fetchSpot(spotId);
    }
  },
  methods: {
    deleteSpot() {
      const token = localStorage.getItem('access_token');
      fetch(`http://localhost:5000/admin/spot/${this.local.id}`, {
        method: 'DELETE',
        headers: {
          'Authorization': 'Bearer ' + token
        }
      })
        .then(response => {
          if (!response.ok) {
            throw new Error("Failed to delete spot.");
          }
          alert("Spot deleted successfully.");
          this.$router.push('/admin'); // Redirect after deletion
        })
        .catch(error => {
          console.error("Delete error:", error);
          alert("Error deleting spot.");
        });
    },
    fetchSpot(spotId) {
      const token = localStorage.getItem('access_token');
      fetch(`http://localhost:5000/admin/spot/${spotId}`, {
        headers: {
          'Authorization': 'Bearer ' + token
        }
      })
        .then(res => {
          if (!res.ok) throw new Error("Failed to fetch spot details");
          return res.json();
        })
        .then(data => {
          this.local.id = data.id;
          this.local.status = data.status;
          this.local.customerId = data.customer_id;
          this.local.vehicleNumber = data.vehicle_number;
          this.local.reservedAt = data.reserved_at;
          this.local.leaveAt = data.leave_at;
          this.local.cost = data.cost;
        })
        .catch(error => {
          console.error("Fetch error:", error);
        });
    },
    close() {
      // Close panel or navigate elsewhere
      this.$router.go(-1);
    },
    showOccupiedDetails() {
      this.showDetails = true;
    },
    closeDetails() {
      this.showDetails = false;
    }
  }
};
</script>

<style scoped>
.header {
  font-weight: bold;
  background: #ffe599;
  border-radius: 9px 9px 0 0;
  padding: 10px;
  margin-bottom: 14px;
  font-size: 1.08em;
  text-align: left;
}
.parking-spot-container,
.occupied-details-container {
  border: 2px solid #222;
  border-radius: 14px;
  padding: 22px 28px 18px 28px;
  margin: 15px;
  background: #fff;
  min-width: 330px;
  box-shadow: 0 3px 12px #ccc4;
}
.field-row {
  display: flex;
  align-items: center;
  margin-bottom: 13px;
}
.field-row label {
  width: 170px;
  font-weight: 500;
}
.value-box {
  min-width: 80px;
  display: inline-block;
  border: 2px solid #ff9900;
  background: #fffbe6;
  font-weight: 700;
  text-align: center;
  padding: 6px 16px;
  font-size: 1.1em;
  border-radius: 6px;
  color: #e08f13;
  margin-left: 10px;
}
.status-btn {
  font-weight: bold;
  border: 2px solid #e08f13;
  border-radius: 5px;
  font-size: 1.18em;
  padding: 2px 17px;
  margin-left: 8px;
  cursor: pointer;
  background: #fffbe6;
  color: #e08f13;
  transition: box-shadow 0.1s;
}
.status-btn.occupied {
  background: #ffe2b1;
  color: #be3900;
  border-color: #be3900;
}
.status-btn.available {
  background: #eaffed;
  color: #159d4c;
  border-color: #009200;
}
.etc-fields {
  margin: 14px 0 8px 14px;
  color: #db4848;
  font-size: 0.97em;
  letter-spacing: 0.01em;
  font-family: 'Comic Sans MS', cursive, sans-serif;
}
.btn-row {
  margin-top: 13px;
  display: flex;
  justify-content: left;
  gap: 21px;
}
.delete-btn {
  background: #e1f0fc;
  color: #186fc1;
  padding: 8px 27px;
  font-weight: bold;
  border-radius: 6px;
  border: 1px solid #b6d0e5;
  font-size: 1.07em;
  cursor: pointer;
  margin-right: 8px;
  transition: background .15s, color .15s;
}
.delete-btn:disabled {
  background: #eee;
  color: #adabab;
  border: 1px solid #bbb;
  cursor: not-allowed;
}
.close-btn {
  background: #e1f0fc;
  color: #186fc1;
  border-radius: 6px;
  border: 1px solid #b6d0e5;
  font-size: 1.07em;
  cursor: pointer;
  padding: 8px 27px;
  font-weight: bold;
}
.note {
  color: #d8000c;
  font-size: 1em;
  margin-top: 12px;
  margin-left: 5px;
  font-family: 'Comic Sans MS', cursive, sans-serif;
}
</style>
