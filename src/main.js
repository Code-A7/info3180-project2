/**
 * Main application entry point
 *
 * This file initializes the Vue application, sets up routing,
 * handles dark mode preferences, and manages service worker registration.
 */

import { createApp } from "vue";
import App from "./App.vue";
import router from "./router";
import socketService from "./services/socketService";
import "./assets/base.css";

const app = createApp(App);

/**
 * Initialize dark mode based on user preference or system settings
 *
 * Checks localStorage for saved theme preference, falls back to system preference
 * if no saved preference exists.
 */
const initDarkMode = () => {
  const savedTheme = localStorage.getItem("theme");

  if (savedTheme === "dark") {
    document.documentElement.classList.add("dark");
  } else if (savedTheme === "light") {
    document.documentElement.classList.remove("dark");
  } else {
    if (window.matchMedia("(prefers-color-scheme: dark)").matches) {
      document.documentElement.classList.add("dark");
    }
  }
};

initDarkMode();

/**
 * Listen for system dark mode preference changes
 *
 * Updates the dark mode setting when the system preference changes,
 * but only if the user hasn't explicitly set a theme preference.
 */
window
  .matchMedia("(prefers-color-scheme: dark)")
  .addEventListener("change", (e) => {
    const savedTheme = localStorage.getItem("theme");
    if (savedTheme === "system" || !savedTheme) {
      document.documentElement.classList.toggle("dark", e.matches);
    }
  });

app.use(router);

/**
 * Register service worker for production builds
 *
 * Enables offline capabilities and caching for the application
 * when running in production mode.
 */
if ("serviceWorker" in navigator && import.meta.env.PROD) {
  window.addEventListener("load", () => {
    navigator.serviceWorker
      .register("/sw.js")
      .then((registration) => {
        console.log("SW registered:", registration);
      })
      .catch((error) => {
        console.log("SW registration failed:", error);
      });
  });
}

/**
 * Initialize socket connection if user is logged in
 *
 * Checks for user data in localStorage and establishes
 * WebSocket connection if user is authenticated.
 */
const user = JSON.parse(localStorage.getItem("user"));
if (user) {
  socketService.connect();
}

/**
 * Mount the Vue application to the DOM
 */
app.mount("#app");
