<template>
  <div
    class="min-h-[calc(100vh-4rem)] flex items-center justify-center px-4 py-12"
  >
    <div class="w-full max-w-md">
      <!-- Card -->
      <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-8">
        <!-- Header -->
        <div class="text-center mb-8">
          <div
            class="w-16 h-16 mx-auto mb-4 rounded-full bg-gradient-to-br from-primary-500 to-accent-500 flex items-center justify-center"
          >
            <span class="text-white font-bold text-2xl">D</span>
          </div>
          <h1 class="text-2xl font-bold text-gray-900 dark:text-white mb-2">
            Welcome Back
          </h1>
          <p class="text-gray-600 dark:text-gray-400">
            Sign in to continue to DriftDater
          </p>
        </div>

        <!-- Success Alert -->
        <div
          v-if="successMessage"
          class="mb-6 p-4 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-xl"
        >
          <p class="text-sm text-green-600 dark:text-green-400">
            {{ successMessage }}
          </p>
        </div>

        <!-- Error Alert -->
        <div
          v-if="error"
          class="mb-6 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-xl"
        >
          <div class="flex items-start gap-3">
            <svg
              class="w-5 h-5 text-red-600 dark:text-red-400 flex-shrink-0 mt-0.5"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
            <div class="flex-1">
              <p class="text-sm text-red-600 dark:text-red-400">
                {{ error }}
              </p>
              <button
                v-if="showResendVerification"
                class="mt-2 text-sm font-medium text-primary-600 dark:text-primary-400 hover:text-primary-700 dark:hover:text-primary-300 underline"
                @click="handleResendVerification"
              >
                Resend verification email
              </button>
            </div>
          </div>
        </div>

        <!-- Form -->
        <form class="space-y-5" @submit.prevent="handleLogin">
          <!-- Email -->
          <div>
            <label
              for="email"
              class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5"
            >
              Email Address
            </label>
            <input
              id="email"
              v-model="email"
              type="email"
              placeholder="you@example.com"
              :disabled="loading"
              required
              class="w-full px-4 py-3 bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl text-gray-900 dark:text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all disabled:opacity-50 disabled:cursor-not-allowed"
              :class="{
                'border-red-500 dark:border-red-400': errors.email,
              }"
            />
            <p v-if="errors.email" class="mt-1.5 text-sm text-red-500">
              {{ errors.email }}
            </p>
          </div>

          <!-- Password -->
          <div>
            <label
              for="password"
              class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5"
            >
              Password
            </label>
            <div class="relative">
              <input
                id="password"
                v-model="password"
                :type="showPassword ? 'text' : 'password'"
                placeholder="Enter your password"
                :disabled="loading"
                required
                class="w-full px-4 py-3 pr-12 bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl text-gray-900 dark:text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                :class="{
                  'border-red-500 dark:border-red-400': errors.password,
                }"
              />
              <button
                type="button"
                class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors"
                tabindex="-1"
                @click="showPassword = !showPassword"
              >
                <svg
                  v-if="!showPassword"
                  class="w-5 h-5"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
                  />
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"
                  />
                </svg>
                <svg
                  v-else
                  class="w-5 h-5"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21"
                  />
                </svg>
              </button>
            </div>
            <p v-if="errors.password" class="mt-1.5 text-sm text-red-500">
              {{ errors.password }}
            </p>
          </div>

          <!-- Remember Me & Forgot Password -->
          <div class="flex items-center justify-between">
            <label class="flex items-center cursor-pointer">
              <input
                v-model="rememberMe"
                type="checkbox"
                :disabled="loading"
                class="w-4 h-4 text-primary-600 bg-gray-100 dark:bg-gray-700 border-gray-300 dark:border-gray-600 rounded focus:ring-primary-500 focus:ring-2 disabled:opacity-50 disabled:cursor-not-allowed"
              />
              <span class="ml-2 text-sm text-gray-700 dark:text-gray-300"
                >Remember me</span
              >
            </label>
            <button
              type="button"
              class="text-sm font-medium text-primary-600 dark:text-primary-400 hover:text-primary-700 dark:hover:text-primary-300 transition-colors"
              @click="showForgotPasswordModal = true"
            >
              Forgot password?
            </button>
          </div>

          <!-- Submit Button -->
          <button
            type="submit"
            :disabled="loading"
            class="w-full py-3.5 px-6 bg-gradient-to-r from-primary-500 to-primary-600 hover:from-primary-600 hover:to-primary-700 text-white font-semibold rounded-xl transition-all duration-300 shadow-lg hover:shadow-xl disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
          >
            <svg
              v-if="loading"
              class="animate-spin -ml-1 mr-2 h-5 w-5"
              fill="none"
              viewBox="0 0 24 24"
            >
              <circle
                class="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                stroke-width="4"
              />
              <path
                class="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
              />
            </svg>
            {{ loading ? "Signing in..." : "Sign In" }}
          </button>
        </form>

        <!-- Divider -->
        <div class="relative my-8">
          <div class="absolute inset-0 flex items-center">
            <div
              class="w-full border-t border-gray-200 dark:border-gray-700"
            ></div>
          </div>
          <div class="relative flex justify-center text-sm">
            <span class="px-4 bg-white dark:bg-gray-800 text-gray-500">or</span>
          </div>
        </div>

        <!-- Register Link -->
        <p class="text-center text-gray-600 dark:text-gray-400">
          Don't have an account?
          <router-link
            to="/register"
            class="font-medium text-primary-600 hover:text-primary-700 dark:text-primary-400 dark:hover:text-primary-300"
          >
            Sign up free
          </router-link>
        </p>
      </div>
    </div>

    <!-- Forgot Password Modal -->
    <div
      v-if="showForgotPasswordModal"
      class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm"
      @click.self="showForgotPasswordModal = false"
    >
      <div
        class="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl p-6 w-full max-w-md"
        @click.stop
      >
        <div class="text-center mb-6">
          <div
            class="w-16 h-16 mx-auto mb-4 rounded-full bg-gradient-to-br from-primary-500 to-accent-500 flex items-center justify-center"
          >
            <svg
              class="w-8 h-8 text-white"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z"
              />
            </svg>
          </div>
          <h2 class="text-xl font-bold text-gray-900 dark:text-white mb-2">
            Reset Password
          </h2>
          <p class="text-gray-600 dark:text-gray-400 text-sm">
            Enter your email and we'll send you a link to reset your password
          </p>
        </div>

        <div
          v-if="forgotPasswordSuccess"
          class="mb-4 p-4 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-xl"
        >
          <p class="text-sm text-green-600 dark:text-green-400">
            Password reset link sent! Check your email inbox.
          </p>
        </div>

        <div
          v-if="forgotPasswordError"
          class="mb-4 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-xl"
        >
          <p class="text-sm text-red-600 dark:text-red-400">
            {{ forgotPasswordError }}
          </p>
        </div>

        <form class="space-y-4" @submit.prevent="handleForgotPassword">
          <div>
            <label
              for="resetEmail"
              class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5"
            >
              Email Address
            </label>
            <input
              id="resetEmail"
              v-model="resetEmail"
              type="email"
              placeholder="you@example.com"
              :disabled="forgotPasswordLoading"
              required
              class="w-full px-4 py-3 bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl text-gray-900 dark:text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            />
          </div>

          <div class="flex gap-3">
            <button
              type="button"
              :disabled="forgotPasswordLoading"
              class="flex-1 py-3 px-4 bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-300 font-medium rounded-xl transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              @click="showForgotPasswordModal = false"
            >
              Cancel
            </button>
            <button
              type="submit"
              :disabled="forgotPasswordLoading"
              class="flex-1 py-3 px-4 bg-gradient-to-r from-primary-500 to-primary-600 hover:from-primary-600 hover:to-primary-700 text-white font-medium rounded-xl transition-all shadow-lg disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
            >
              <svg
                v-if="forgotPasswordLoading"
                class="animate-spin -ml-1 mr-2 h-4 w-4"
                fill="none"
                viewBox="0 0 24 24"
              >
                <circle
                  class="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  stroke-width="4"
                />
                <path
                  class="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                />
              </svg>
              {{ forgotPasswordLoading ? "Sending..." : "Send Link" }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { useRouter, useRoute } from "vue-router";
import { useAuth } from "../composables/useAuth";
import authService, { validateEmail } from "../services/authService";

const router = useRouter();
const route = useRoute();
const { login } = useAuth();

const email = ref("");
const password = ref("");
const rememberMe = ref(false);
const loading = ref(false);
const error = ref("");
const successMessage = ref("");
const showPassword = ref(false);
const showResendVerification = ref(false);
const errors = ref({});

// Forgot password state
const showForgotPasswordModal = ref(false);
const resetEmail = ref("");
const forgotPasswordLoading = ref(false);
const forgotPasswordSuccess = ref(false);
const forgotPasswordError = ref("");

const handleLogin = async () => {
  error.value = "";
  successMessage.value = "";
  errors.value = {};
  loading.value = true;

  try {
    // Validate email
    if (!validateEmail(email.value)) {
      errors.value.email = "Please enter a valid email address";
      loading.value = false;
      return;
    }

    // Validate password
    if (!password.value) {
      errors.value.password = "Password is required";
      loading.value = false;
      return;
    }

    await login(email.value, password.value, rememberMe.value);

    const redirect = route.query.redirect || "/";
    router.push(redirect);
  } catch (err) {
    const errorMsg = err.message || err.response?.data?.errors?.general?.[0];

    if (errorMsg && errorMsg.includes("verify")) {
      error.value =
        "Your email is not verified. Please check your inbox for the verification email.";
      showResendVerification.value = true;
    } else if (err.response?.data?.errors?.general) {
      error.value = err.response.data.errors.general[0];
    } else {
      error.value = errorMsg || "Login failed. Please check your credentials.";
    }
  } finally {
    loading.value = false;
  }
};

const handleResendVerification = async () => {
  if (!validateEmail(email.value)) {
    error.value = "Please enter a valid email address";
    return;
  }

  loading.value = true;
  error.value = "";

  try {
    await authService.resendVerification(email.value);
    successMessage.value = "Verification email sent! Please check your inbox.";
    showResendVerification.value = false;
  } catch (err) {
    error.value = err.message || "Failed to resend verification email";
  } finally {
    loading.value = false;
  }
};

const handleForgotPassword = async () => {
  if (!validateEmail(resetEmail.value)) {
    forgotPasswordError.value = "Please enter a valid email address";
    return;
  }

  forgotPasswordLoading.value = true;
  forgotPasswordError.value = "";
  forgotPasswordSuccess.value = false;

  try {
    await authService.forgotPassword(resetEmail.value);
    forgotPasswordSuccess.value = true;

    // Auto-close modal after success
    setTimeout(() => {
      showForgotPasswordModal.value = false;
      forgotPasswordSuccess.value = false;
      resetEmail.value = "";
    }, 3000);
  } catch (err) {
    forgotPasswordError.value = err.message || "Failed to send reset link";
  } finally {
    forgotPasswordLoading.value = false;
  }
};

// Check for success message from registration redirect
onMounted(() => {
  if (route.query.registered === "true") {
    successMessage.value =
      "Registration successful! Please check your email to verify your account.";
  }
});
</script>
