import { createApp } from "vue";
import App from "./App.vue";
import router from "./router";
import socketService from "./services/socketService";
import "./assets/base.css";

const app = createApp(App);

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

window
  .matchMedia("(prefers-color-scheme: dark)")
  .addEventListener("change", (e) => {
    const savedTheme = localStorage.getItem("theme");
    if (savedTheme === "system" || !savedTheme) {
      document.documentElement.classList.toggle("dark", e.matches);
    }
  });

app.use(router);

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

const user = JSON.parse(localStorage.getItem("user"));
if (user) {
  socketService.connect();
}

app.mount("#app");
