<template>
  <div
    class="min-h-[calc(100vh-4rem)] flex items-center justify-center px-4 py-12"
  >
    <div class="w-full max-w-md">
      <!-- Success State -->
      <div
        v-if="showSuccess"
        class="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-8 text-center"
      >
        <div
          class="w-20 h-20 mx-auto mb-6 rounded-full bg-green-100 dark:bg-green-900/30 flex items-center justify-center"
        >
          <svg
            class="w-10 h-10 text-green-500"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M5 13l4 4L19 7"
            />
          </svg>
        </div>
        <h1 class="text-2xl font-bold text-gray-900 dark:text-white mb-3">
          Registration Successful!
        </h1>
        <p class="text-gray-600 dark:text-gray-400 mb-6">
          {{ successMessage }}
        </p>
        <div class="flex gap-3">
          <router-link
            to="/login"
            class="flex-1 py-3.5 px-6 bg-gradient-to-r from-primary-500 to-primary-600 hover:from-primary-600 hover:to-primary-700 text-white font-semibold rounded-xl transition-all duration-300"
          >
            Go to Login
          </router-link>
          <button
            :disabled="resendLoading"
            class="flex-1 py-3.5 px-6 bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-300 font-semibold rounded-xl transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed"
            @click="handleResendVerification"
          >
            {{ resendLoading ? "Sending..." : "Resend Email" }}
          </button>
        </div>
      </div>

      <!-- Register Form -->
      <div v-else class="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-8">
        <!-- Header -->
        <div class="text-center mb-8">
          <div
            class="w-16 h-16 mx-auto mb-4 rounded-full bg-gradient-to-br from-primary-500 to-accent-500 flex items-center justify-center"
          >
            <span class="text-white font-bold text-2xl">D</span>
          </div>
          <h1 class="text-2xl font-bold text-gray-900 dark:text-white mb-2">
            Join DriftDater
          </h1>
          <p class="text-gray-600 dark:text-gray-400">
            Find your perfect match today
          </p>
        </div>

        <!-- Error Alert -->
        <div
          v-if="errors.general"
          class="mb-6 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-xl"
        >
          <p class="text-sm text-red-600 dark:text-red-400">
            {{ errors.general[0] }}
          </p>
        </div>

        <!-- Form -->
        <form class="space-y-5" @submit.prevent="handleRegister">
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
                'border-green-500 dark:border-green-400': emailValid,
              }"
              @blur="validateEmailField"
            />
            <p v-if="errors.email" class="mt-1.5 text-sm text-red-500">
              {{ errors.email }}
            </p>
            <p v-if="emailValid" class="mt-1.5 text-sm text-green-500">
              Email looks good!
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
                placeholder="Create a strong password"
                :disabled="loading"
                required
                class="w-full px-4 py-3 pr-12 bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl text-gray-900 dark:text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                :class="{
                  'border-red-500 dark:border-red-400':
                    errors.password && password,
                  'border-green-500 dark:border-green-400': passwordValid,
                }"
                @input="validatePassword"
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

            <!-- Password Strength Indicator -->
            <div v-if="password" class="mt-2 space-y-2">
              <div class="flex gap-1">
                <div
                  v-for="i in 3"
                  :key="i"
                  class="h-1.5 flex-1 rounded-full transition-all duration-300"
                  :class="getStrengthClass(i)"
                ></div>
              </div>
              <p class="text-xs" :class="strengthTextClass">
                Password strength: {{ passwordStrength }}
              </p>

              <!-- Password Requirements -->
              <div class="mt-2 p-3 bg-gray-50 dark:bg-gray-900 rounded-lg">
                <p
                  class="text-xs font-medium text-gray-700 dark:text-gray-300 mb-2"
                >
                  Password must contain:
                </p>
                <ul class="space-y-1">
                  <li
                    class="flex items-center gap-2 text-xs"
                    :class="
                      passwordRequirements.length
                        ? 'text-green-600 dark:text-green-400'
                        : 'text-gray-500 dark:text-gray-400'
                    "
                  >
                    <svg
                      v-if="passwordRequirements.length"
                      class="w-3.5 h-3.5"
                      fill="currentColor"
                      viewBox="0 0 20 20"
                    >
                      <path
                        fill-rule="evenodd"
                        d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                        clip-rule="evenodd"
                      />
                    </svg>
                    <svg
                      v-else
                      class="w-3.5 h-3.5"
                      fill="currentColor"
                      viewBox="0 0 20 20"
                    >
                      <path
                        fill-rule="evenodd"
                        d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                        clip-rule="evenodd"
                      />
                    </svg>
                    At least 8 characters
                  </li>
                  <li
                    class="flex items-center gap-2 text-xs"
                    :class="
                      passwordRequirements.uppercase
                        ? 'text-green-600 dark:text-green-400'
                        : 'text-gray-500 dark:text-gray-400'
                    "
                  >
                    <svg
                      v-if="passwordRequirements.uppercase"
                      class="w-3.5 h-3.5"
                      fill="currentColor"
                      viewBox="0 0 20 20"
                    >
                      <path
                        fill-rule="evenodd"
                        d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                        clip-rule="evenodd"
                      />
                    </svg>
                    <svg
                      v-else
                      class="w-3.5 h-3.5"
                      fill="currentColor"
                      viewBox="0 0 20 20"
                    >
                      <path
                        fill-rule="evenodd"
                        d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                        clip-rule="evenodd"
                      />
                    </svg>
                    One uppercase letter
                  </li>
                  <li
                    class="flex items-center gap-2 text-xs"
                    :class="
                      passwordRequirements.number
                        ? 'text-green-600 dark:text-green-400'
                        : 'text-gray-500 dark:text-gray-400'
                    "
                  >
                    <svg
                      v-if="passwordRequirements.number"
                      class="w-3.5 h-3.5"
                      fill="currentColor"
                      viewBox="0 0 20 20"
                    >
                      <path
                        fill-rule="evenodd"
                        d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                        clip-rule="evenodd"
                      />
                    </svg>
                    <svg
                      v-else
                      class="w-3.5 h-3.5"
                      fill="currentColor"
                      viewBox="0 0 20 20"
                    >
                      <path
                        fill-rule="evenodd"
                        d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                        clip-rule="evenodd"
                      />
                    </svg>
                    One number
                  </li>
                  <li
                    class="flex items-center gap-2 text-xs"
                    :class="
                      passwordRequirements.special
                        ? 'text-green-600 dark:text-green-400'
                        : 'text-gray-500 dark:text-gray-400'
                    "
                  >
                    <svg
                      v-if="passwordRequirements.special"
                      class="w-3.5 h-3.5"
                      fill="currentColor"
                      viewBox="0 0 20 20"
                    >
                      <path
                        fill-rule="evenodd"
                        d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                        clip-rule="evenodd"
                      />
                    </svg>
                    <svg
                      v-else
                      class="w-3.5 h-3.5"
                      fill="currentColor"
                      viewBox="0 0 20 20"
                    >
                      <path
                        fill-rule="evenodd"
                        d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                        clip-rule="evenodd"
                      />
                    </svg>
                    One special character
                  </li>
                </ul>
              </div>
            </div>

            <p v-if="errors.password" class="mt-1.5 text-sm text-red-500">
              {{ errors.password }}
            </p>
          </div>

          <!-- Confirm Password -->
          <div>
            <label
              for="confirmPassword"
              class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5"
            >
              Confirm Password
            </label>
            <input
              id="confirmPassword"
              v-model="confirmPassword"
              type="password"
              placeholder="Confirm your password"
              :disabled="loading"
              required
              class="w-full px-4 py-3 bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl text-gray-900 dark:text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all disabled:opacity-50 disabled:cursor-not-allowed"
              :class="{
                'border-red-500 dark:border-red-400': passwordMismatch,
                'border-green-500 dark:border-green-400':
                  passwordsMatch && confirmPassword,
              }"
              @input="validatePasswordMatch"
            />
            <p v-if="passwordMismatch" class="mt-1.5 text-sm text-red-500">
              {{ passwordMismatch }}
            </p>
            <p
              v-if="passwordsMatch && confirmPassword"
              class="mt-1.5 text-sm text-green-500"
            >
              Passwords match!
            </p>
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
            {{ loading ? "Creating Account..." : "Create Account" }}
          </button>
        </form>

        <!-- Login Link -->
        <p class="text-center mt-8 text-gray-600 dark:text-gray-400">
          Already have an account?
          <router-link
            to="/login"
            class="font-medium text-primary-600 hover:text-primary-700 dark:text-primary-400 dark:hover:text-primary-300"
          >
            Sign in
          </router-link>
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from "vue";
import { useRouter } from "vue-router";
import { useAuth } from "../composables/useAuth";
import authService, {
  passwordValidation,
  validateEmail,
} from "../services/authService";

const router = useRouter();
const { register } = useAuth();

const email = ref("");
const password = ref("");
const confirmPassword = ref("");
const loading = ref(false);
const resendLoading = ref(false);
const showSuccess = ref(false);
const successMessage = ref("");
const showPassword = ref(false);
const errors = ref({});

// Validation state
const emailValid = ref(false);
const passwordValid = ref(false);
const passwordsMatch = ref(false);
const passwordStrength = ref("weak");
const passwordRequirements = ref({
  length: false,
  uppercase: false,
  number: false,
  special: false,
});

const passwordMismatch = computed(() => {
  if (confirmPassword.value && password.value !== confirmPassword.value) {
    return "Passwords do not match";
  }
  return "";
});

const strengthTextClass = computed(() => {
  const classes = {
    weak: "text-red-600 dark:text-red-400",
    medium: "text-amber-600 dark:text-amber-400",
    strong: "text-green-600 dark:text-green-400",
  };
  return classes[passwordStrength.value] || classes.weak;
});

const validateEmailField = () => {
  if (!email.value) {
    emailValid.value = false;
    return;
  }

  if (!validateEmail(email.value)) {
    emailValid.value = false;
    errors.value.email = "Please enter a valid email address";
  } else {
    emailValid.value = true;
    errors.value.email = "";
  }
};

const validatePassword = () => {
  if (!password.value) {
    passwordValid.value = false;
    passwordStrength.value = "weak";
    passwordRequirements.value = {
      length: false,
      uppercase: false,
      number: false,
      special: false,
    };
    return;
  }

  const result = passwordValidation.validate(password.value);
  passwordValid.value = result.isValid;
  passwordStrength.value = result.strength;

  // Update requirements
  passwordRequirements.value = {
    length: password.value.length >= 8,
    uppercase: /[A-Z]/.test(password.value),
    number: /[0-9]/.test(password.value),
    special: /[!@#$%^&*(),.?":{}|<>]/.test(password.value),
  };

  // Re-check match
  validatePasswordMatch();
};

const validatePasswordMatch = () => {
  if (!confirmPassword.value) {
    passwordsMatch.value = false;
    return;
  }

  passwordsMatch.value = password.value === confirmPassword.value;
};

const getStrengthClass = (level) => {
  const strengthLevels = { weak: 1, medium: 2, strong: 3 };
  const currentLevel = strengthLevels[passwordStrength.value] || 1;

  const baseClass = "transition-all duration-300";
  const activeClass =
    level <= currentLevel
      ? passwordStrength.value === "weak"
        ? "bg-red-500"
        : passwordStrength.value === "medium"
          ? "bg-amber-500"
          : "bg-green-500"
      : "bg-gray-200 dark:bg-gray-700";

  return `${baseClass} ${activeClass}`;
};

const handleRegister = async () => {
  errors.value = {};

  // Validate all fields
  validateEmailField();
  validatePassword();
  validatePasswordMatch();

  if (!emailValid.value || !passwordValid.value || !passwordsMatch.value) {
    return;
  }

  loading.value = true;

  try {
    await register(email.value, password.value);
    showSuccess.value = true;
    successMessage.value =
      "Please check your email inbox to verify your account before logging in.";
  } catch (err) {
    if (err.response?.data?.errors) {
      errors.value = err.response.data.errors;
    } else {
      errors.value = {
        general: [err.message || "Registration failed. Please try again."],
      };
    }
  } finally {
    loading.value = false;
  }
};

const handleResendVerification = async () => {
  resendLoading.value = true;

  try {
    await authService.resendVerification(email.value);
    successMessage.value =
      "Verification email resent! Please check your inbox.";
  } catch (err) {
    errors.value = {
      general: [err.message || "Failed to resend verification email"],
    };
  } finally {
    resendLoading.value = false;
  }
};

// Watch for password changes to update match validation
watch(password, () => {
  if (confirmPassword.value) {
    validatePasswordMatch();
  }
});
</script>
