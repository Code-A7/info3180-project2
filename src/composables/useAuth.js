import { ref, computed } from "vue";
import authService from "../services/authService";
import socketService from "../services/socketService";

// Reactive state
const currentUser = ref(authService.getStoredUser());
const isLoading = ref(false);
const authError = ref(null);

// Computed
const isAuthenticated = computed(() => !!currentUser.value);
const user = computed(() => currentUser.value);

// Methods
async function login(email, password, rememberMe = false) {
  isLoading.value = true;
  authError.value = null;

  try {
    const response = await authService.login(email, password, rememberMe);
    currentUser.value = response.user;
    return response;
  } catch (error) {
    authError.value = error.message || "Login failed";
    throw error;
  } finally {
    isLoading.value = false;
  }
}

async function register(email, password) {
  isLoading.value = true;
  authError.value = null;

  try {
    const response = await authService.register(email, password);
    return response;
  } catch (error) {
    authError.value = error.message || "Registration failed";
    throw error;
  } finally {
    isLoading.value = false;
  }
}

async function logout() {
  isLoading.value = true;

  try {
    await authService.logout();
    socketService.disconnect();
    currentUser.value = null;
    authError.value = null;
  } catch (error) {
    console.error("Logout error:", error);
  } finally {
    isLoading.value = false;
  }
}

async function verifyEmail(token) {
  isLoading.value = true;
  authError.value = null;

  try {
    const response = await authService.verifyEmail(token);
    return response;
  } catch (error) {
    authError.value = error.message || "Email verification failed";
    throw error;
  } finally {
    isLoading.value = false;
  }
}

async function refreshUser() {
  try {
    const userData = await authService.getCurrentUser();
    currentUser.value = userData;
    return userData;
  } catch (error) {
    currentUser.value = null;
    throw error;
  }
}

function clearError() {
  authError.value = null;
}

export function useAuth() {
  return {
    // State
    currentUser,
    isLoading,
    authError,

    // Computed
    isAuthenticated,
    user,

    // Methods
    login,
    register,
    logout,
    verifyEmail,
    refreshUser,
    clearError,
  };
}

export default useAuth;
