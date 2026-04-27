/**
 * API service with axios configuration
 *
 * This module provides a configured axios instance with:
 * - Request/response interceptors
 * - Automatic token refresh handling
 * - Error handling and retry logic
 * - Authentication state management
 */

import axios from "axios";

// Token refresh state
let isRefreshing = false;
let failedQueue = [];

/**
 * Process queued requests after token refresh
 *
 * @param {Error|null} error - Error from refresh attempt, or null if successful
 * @param {string|null} token - New token if refresh was successful
 */
const processQueue = (error, token = null) => {
  failedQueue.forEach((prom) => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve(token);
    }
  });

  failedQueue = [];
};

/**
 * Get authentication token from storage
 *
 * @returns {string|null} Authentication token or null if not found
 */
const getToken = () => {
  return localStorage.getItem("token") || sessionStorage.getItem("token");
};

/**
 * Get user data from storage
 *
 * @returns {Object|null} Parsed user object or null if not found/invalid
 */
const getUser = () => {
  try {
    const user = localStorage.getItem("user") || sessionStorage.getItem("user");
    return user ? JSON.parse(user) : null;
  } catch (e) {
    console.error("Error parsing stored user:", e);
    return null;
  }
};

/**
 * Clear all authentication data from storage
 */
const clearAuthData = () => {
  localStorage.removeItem("token");
  localStorage.removeItem("user");
  localStorage.removeItem("rememberMe");
  sessionStorage.removeItem("token");
  sessionStorage.removeItem("user");
};

/**
 * Configured axios instance for API requests
 */
const api = axios.create({
  baseURL: "/",
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 30000, // 30 second timeout
  maxRetries: 2,
  retryDelay: 1000,
});

// Request interceptor - add auth token
api.interceptors.request.use(
  /**
   * Add authentication token to requests and track timing
   *
   * @param {Object} config - Axios request configuration
   * @returns {Object} Modified request configuration
   */
  (config) => {
    const token = getToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    // Add request timestamp for debugging
    config.metadata = { startTime: new Date() };

    return config;
  },
  /**
   * Handle request errors
   *
   * @param {Error} error - Request error
   * @returns {Promise} Rejected promise with error
   */
  (error) => {
    console.error("Request error:", error);
    return Promise.reject(error);
  },
);

// Response interceptor - handle errors and token refresh
api.interceptors.response.use(
  (response) => {
    // Log response time for debugging
    if (response.config.metadata) {
      const duration = new Date() - response.config.metadata.startTime;
      if (duration > 5000) {
        console.warn(
          `Slow API response: ${response.config.url} took ${duration}ms`,
        );
      }
    }
    return response;
  },
  async (error) => {
    const originalRequest = error.config;

    // Handle network errors
    if (!error.response) {
      if (error.code === "ECONNABORTED") {
        console.error("Request timeout:", originalRequest.url);
        error.message = "Request timed out. Please try again.";
      } else if (error.code === "ERR_NETWORK") {
        console.error("Network error:", error.message);
        error.message = "Network error. Please check your connection.";
      }
      return Promise.reject(error);
    }

    // Handle 401 Unauthorized - Token expired or invalid
    if (error.response.status === 401) {
      // Prevent infinite loops
      if (originalRequest._retry) {
        clearAuthData();
        // Redirect to login
        if (typeof window !== "undefined") {
          const currentPath = window.location.pathname;
          const redirectParam =
            currentPath !== "/login"
              ? `?redirect=${encodeURIComponent(currentPath)}`
              : "";
          window.location.href = `/login${redirectParam}`;
        }
        return Promise.reject(error);
      }

      // If already trying to refresh, queue this request
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        })
          .then((token) => {
            originalRequest.headers.Authorization = `Bearer ${token}`;
            return api(originalRequest);
          })
          .catch((err) => Promise.reject(err));
      }

      originalRequest._retry = true;
      isRefreshing = true;

      try {
        // Try to refresh the token
        const user = getUser();
        if (user?.id) {
          const refreshResponse = await axios.post(
            "/api/auth/refresh",
            {
              user_id: user.id,
            },
            {
              headers: {
                "Content-Type": "application/json",
              },
            },
          );

          if (refreshResponse.data.token) {
            const newToken = refreshResponse.data.token;

            // Store new token
            const rememberMe = localStorage.getItem("rememberMe");
            if (rememberMe) {
              localStorage.setItem("token", newToken);
              localStorage.setItem(
                "user",
                JSON.stringify(refreshResponse.data.user || user),
              );
            } else {
              sessionStorage.setItem("token", newToken);
              sessionStorage.setItem(
                "user",
                JSON.stringify(refreshResponse.data.user || user),
              );
              localStorage.setItem("token", newToken);
              localStorage.setItem(
                "user",
                JSON.stringify(refreshResponse.data.user || user),
              );
            }

            // Process queued requests
            processQueue(null, newToken);

            // Retry original request with new token
            originalRequest.headers.Authorization = `Bearer ${newToken}`;
            return api(originalRequest);
          }
        }
      } catch (refreshError) {
        // Refresh failed - clear auth and redirect
        clearAuthData();
        processQueue(refreshError, null);

        if (typeof window !== "undefined") {
          const currentPath = window.location.pathname;
          const redirectParam =
            currentPath !== "/login"
              ? `?redirect=${encodeURIComponent(currentPath)}`
              : "";
          window.location.href = `/login${redirectParam}`;
        }
      } finally {
        isRefreshing = false;
      }
    }

    // Handle 403 Forbidden
    if (error.response.status === 403) {
      console.warn("Access forbidden:", error.response.data);
      error.message =
        error.response.data?.error ||
        "You do not have permission to perform this action.";
    }

    // Handle 404 Not Found
    if (error.response.status === 404) {
      console.warn("Resource not found:", originalRequest.url);
      error.message = "The requested resource was not found.";
    }

    // Handle 500 Server Error
    if (error.response.status === 500) {
      console.error("Server error:", error.response.data);
      error.message = "A server error occurred. Please try again later.";
    }

    // Handle validation errors (422)
    if (error.response.status === 422 && error.response.data?.errors) {
      error.validationErrors = error.response.data.errors;
    }

    return Promise.reject(error);
  },
);

// Add retry logic for failed requests
const retryRequest = async (config, retriesLeft) => {
  try {
    return await api(config);
  } catch (error) {
    if (retriesLeft > 0 && (!error.response || error.response.status >= 500)) {
      await new Promise((resolve) =>
        setTimeout(resolve, config.retryDelay || 1000),
      );
      return retryRequest(config, retriesLeft - 1);
    }
    throw error;
  }
};

// Wrapper methods with retry support
export const apiWithRetry = {
  get: async (url, config = {}) => {
    return retryRequest(
      { ...config, method: "GET", url },
      config.maxRetries ?? api.defaults.maxRetries,
    );
  },
  post: async (url, data, config = {}) => {
    return retryRequest(
      { ...config, method: "POST", url, data },
      config.maxRetries ?? api.defaults.maxRetries,
    );
  },
  put: async (url, data, config = {}) => {
    return retryRequest(
      { ...config, method: "PUT", url, data },
      config.maxRetries ?? api.defaults.maxRetries,
    );
  },
  delete: async (url, config = {}) => {
    return retryRequest(
      { ...config, method: "DELETE", url },
      config.maxRetries ?? api.defaults.maxRetries,
    );
  },
  patch: async (url, data, config = {}) => {
    return retryRequest(
      { ...config, method: "PATCH", url, data },
      config.maxRetries ?? api.defaults.maxRetries,
    );
  },
};

export { getToken, getUser, clearAuthData };
export default api;
