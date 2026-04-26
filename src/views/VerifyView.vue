<template>
  <div class="verify-container">
    <div class="verify-card">
      <div v-if="loading" class="loading">Verifying your email...</div>

      <div v-else-if="success" class="success">
        <div class="icon">✓</div>
        <h2>Email Verified!</h2>
        <p>
          Your email has been successfully verified. You can now login to your
          account.
        </p>
        <router-link to="/login" class="btn-primary">Login</router-link>
      </div>

      <div v-else class="error">
        <div class="icon">✕</div>
        <h2>Verification Failed</h2>
        <p>{{ errorMessage }}</p>
        <router-link to="/register" class="btn-primary"
          >Register Again</router-link
        >
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRoute } from "vue-router";
import authService from "../services/authService";

const route = useRoute();
const loading = ref(true);
const success = ref(false);
const errorMessage = ref("");

const verifyEmail = async () => {
  const token = route.params.token;

  if (!token) {
    success.value = false;
    errorMessage.value = "Invalid verification link.";
    loading.value = false;
    return;
  }

  try {
    await authService.verifyEmail(token);
    success.value = true;
  } catch (error) {
    success.value = false;
    if (error.response?.status === 404) {
      errorMessage.value = "Invalid or expired verification token.";
    } else {
      errorMessage.value = "Verification failed. Please try again.";
    }
  } finally {
    loading.value = false;
  }
};

onMounted(verifyEmail);
</script>

<style scoped>
.verify-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 80vh;
  padding: 20px;
}

.verify-card {
  background: white;
  padding: 50px;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  text-align: center;
  max-width: 400px;
}

.loading {
  color: #666;
  font-size: 18px;
}

.success .icon,
.error .icon {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 40px;
  margin: 0 auto 20px;
}

.success .icon {
  background: #e8f5e9;
  color: #4caf50;
}

.error .icon {
  background: #ffebee;
  color: #e53935;
}

h2 {
  margin: 0 0 15px 0;
}

.success h2 {
  color: #4caf50;
}

.error h2 {
  color: #e53935;
}

p {
  color: #666;
  margin-bottom: 30px;
  line-height: 1.6;
}

.btn-primary {
  display: inline-block;
  padding: 14px 30px;
  background: #e91e63;
  color: white;
  text-decoration: none;
  border-radius: 6px;
  font-weight: 600;
}
</style>
