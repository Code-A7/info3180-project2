/**
 * Authentication service
 *
 * This module provides authentication-related utilities including
 * password validation, user registration, login, and token management.
 */

import api from "./api";

// Password validation utilities
export const passwordValidation = {
  /**
   * Minimum password length requirement
   */
  minLength: 8,

  /**
   * Regular expression patterns for password complexity requirements
   */
  patterns: {
    uppercase: /[A-Z]/,
    lowercase: /[a-z]/,
    number: /[0-9]/,
    special: /[!@#$%^&*(),.?":{}|<>]/,
  },

  /**
   * Validate password against complexity requirements
   *
   * @param {string} password - Password to validate
   * @returns {Object} Validation result with isValid, errors, and strength
   */
  validate(password) {
    const errors = [];

    if (password.length < this.minLength) {
      errors.push(
        `Password must be at least ${this.minLength} characters long`,
      );
    }
    if (!this.patterns.uppercase.test(password)) {
      errors.push("Password must contain at least one uppercase letter");
    }
    if (!this.patterns.lowercase.test(password)) {
      errors.push("Password must contain at least one lowercase letter");
    }
    if (!this.patterns.number.test(password)) {
      errors.push("Password must contain at least one number");
    }
    if (!this.patterns.special.test(password)) {
      errors.push("Password must contain at least one special character");
    }

    return {
      isValid: errors.length === 0,
      errors,
      strength: this.calculateStrength(password),
    };
  },

  /**
   * Calculate password strength score
   *
   * @param {string} password - Password to evaluate
   * @returns {number} Strength score (0-7)
   */
  calculateStrength(password) {
    let score = 0;
    if (password.length >= 8) score++;
    if (password.length >= 12) score++;
    if (password.length >= 16) score++;
    if (this.patterns.uppercase.test(password)) score++;
    if (this.patterns.lowercase.test(password)) score++;
    if (this.patterns.number.test(password)) score++;
    if (this.patterns.special.test(password)) score++;

    if (score <= 3) return "weak";
    if (score <= 5) return "medium";
    return "strong";
  },
};

// Email validation
export const validateEmail = (email) => {
  const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return re.test(email);
};

export const authService = {
  /**
   * Register a new user
   * @param {string} email - User email
   * @param {string} password - User password
   * @returns {Promise<object>} Registration response
   */
  async register(email, password) {
    // Validate email
    if (!validateEmail(email)) {
      throw new Error("Please enter a valid email address");
    }

    // Validate password strength
    const passwordCheck = passwordValidation.validate(password);
    if (!passwordCheck.isValid) {
      throw new Error(passwordCheck.errors[0]);
    }

    const response = await api.post("/api/auth/register", {
      email,
      password,
      confirm_password: password,
    });
    return response.data;
  },

  /**
   * Login user
   * @param {string} email - User email
   * @param {string} password - User password
   * @param {boolean} rememberMe - Whether to persist login
   * @returns {Promise<object>} Login response with token and user data
   */
  async login(email, password, rememberMe = false) {
    // Validate inputs
    if (!email || !password) {
      throw new Error("Please enter both email and password");
    }

    if (!validateEmail(email)) {
      throw new Error("Please enter a valid email address");
    }

    const response = await api.post("/api/auth/login", {
      email,
      password,
      remember_me: rememberMe,
    });

    // Handle specific error messages
    if (response.data.errors?.general) {
      const errorMsg = response.data.errors.general[0];
      if (errorMsg.includes("verify")) {
        throw new Error(
          "Please verify your email first. Check your Mailtrap inbox for the verification link.",
        );
      }
      throw new Error(errorMsg);
    }

    if (response.data.token) {
      this.storeAuthData(response.data.token, response.data.user, rememberMe);
    }
    return response.data;
  },

  /**
   * Logout user
   * Clears local storage and notifies backend
   */
  async logout() {
    try {
      await api.post("/api/auth/logout");
    } catch (e) {
      // Continue with local cleanup even if backend call fails
      console.warn("Logout API call failed, but cleaning up local data");
    } finally {
      this.clearAuthData();
    }
  },

  /**
   * Get current authenticated user
   * @returns {Promise<object>} Current user data
   */
  async getCurrentUser() {
    const response = await api.get("/api/auth/me");

    // Update stored user data if successful
    if (response.data) {
      localStorage.setItem("user", JSON.stringify(response.data));
    }

    return response.data;
  },

  /**
   * Verify email with token
   * @param {string} token - Verification token
   * @returns {Promise<object>} Verification response
   */
  async verifyEmail(token) {
    if (!token) {
      throw new Error("Invalid verification token");
    }

    const response = await api.get(`/api/auth/verify/${token}`);
    return response.data;
  },

  /**
   * Resend verification email
   * @param {string} email - User email
   * @returns {Promise<object>} Response
   */
  async resendVerification(email) {
    if (!validateEmail(email)) {
      throw new Error("Please enter a valid email address");
    }

    const response = await api.post("/api/auth/resend-verification", {
      email,
    });
    return response.data;
  },

  /**
   * Request password reset
   * @param {string} email - User email
   * @returns {Promise<object>} Response
   */
  async forgotPassword(email) {
    if (!validateEmail(email)) {
      throw new Error("Please enter a valid email address");
    }

    const response = await api.post("/api/auth/forgot-password", {
      email,
    });
    return response.data;
  },

  /**
   * Reset password with token
   * @param {string} token - Reset token
   * @param {string} newPassword - New password
   * @returns {Promise<object>} Response
   */
  async resetPassword(token, newPassword) {
    const passwordCheck = passwordValidation.validate(newPassword);
    if (!passwordCheck.isValid) {
      throw new Error(passwordCheck.errors[0]);
    }

    const response = await api.post("/api/auth/reset-password", {
      token,
      password: newPassword,
      confirm_password: newPassword,
    });
    return response.data;
  },

  /**
   * Get stored user from localStorage
   * @returns {object|null} Stored user data or null
   */
  getStoredUser() {
    try {
      const user = localStorage.getItem("user");
      return user ? JSON.parse(user) : null;
    } catch (e) {
      console.error("Error parsing stored user:", e);
      localStorage.removeItem("user");
      return null;
    }
  },

  /**
   * Check if user is authenticated
   * @returns {boolean} True if authenticated
   */
  isAuthenticated() {
    const token = localStorage.getItem("token");
    return !!token;
  },

  /**
   * Get stored token
   * @returns {string|null} Token or null
   */
  getToken() {
    return localStorage.getItem("token");
  },

  /**
   * Store authentication data
   * @private
   */
  storeAuthData(token, user, rememberMe) {
    try {
      if (rememberMe) {
        // Set with longer expiry (30 days)
        localStorage.setItem("token", token);
        localStorage.setItem("user", JSON.stringify(user));
        localStorage.setItem("rememberMe", "true");
      } else {
        // Session storage for tab session
        sessionStorage.setItem("token", token);
        sessionStorage.setItem("user", JSON.stringify(user));
        // Also store in localStorage for redundancy
        localStorage.setItem("token", token);
        localStorage.setItem("user", JSON.stringify(user));
        localStorage.removeItem("rememberMe");
      }
    } catch (e) {
      console.error("Error storing auth data:", e);
      throw new Error("Failed to store authentication data", { cause: e });
    }
  },

  /**
   * Clear authentication data
   * @private
   */
  clearAuthData() {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    localStorage.removeItem("rememberMe");
    sessionStorage.removeItem("token");
    sessionStorage.removeItem("user");
  },
};

export default authService;
