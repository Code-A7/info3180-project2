/**
 * WebSocket service for real-time communication
 *
 * This module handles WebSocket connections, event handling,
 * and browser notifications for real-time features like
 * messages, matches, and notifications.
 */

import { io } from "socket.io-client";
import authService from "./authService";

let socket = null;

/**
 * Request browser notification permission
 */
const requestNotificationPermission = async () => {
  if ("Notification" in window && Notification.permission === "default") {
    await Notification.requestPermission();
  }
};

/**
 * Show browser notification
 *
 * @param {string} title - Notification title
 * @param {string} body - Notification body text
 * @param {string} icon - Optional notification icon URL
 */
const showNotification = (title, body, icon) => {
  if ("Notification" in window && Notification.permission === "granted") {
    new Notification(title, {
      body,
      icon: icon || "/icon-192.png",
    });
  }
};

export const socketService = {
  /**
   * Connect to WebSocket server
   *
   * @returns {Object} Socket instance
   */
  connect() {
    if (socket?.connected) return socket;

    const SOCKET_BASE_URL =
      import.meta.env.VITE_API_BASE_URL || "http://localhost:5000";
    socket = io(SOCKET_BASE_URL, {
      transports: ["websocket", "polling"],
      autoConnect: true,
    });

    socket.on("connect", () => {
      console.log("Socket connected:", socket.id);

      requestNotificationPermission();

      const user = authService.getStoredUser();
      if (user) {
        socket.emit("subscribe", { user_id: user.id });
      }
    });

    socket.on("disconnect", () => {
      console.log("Socket disconnected");
    });

    socket.on("connect_error", (error) => {
      console.error("Socket connection error:", error);
    });

    socket.on("new_message", (data) => {
      const user = authService.getStoredUser();
      if (user && data.sender_id !== user.id) {
        showNotification(
          data.sender_name || "New Message",
          data.content.substring(0, 100),
        );
      }
    });

    return socket;
  },

  disconnect() {
    if (socket) {
      const user = authService.getStoredUser();
      if (user) {
        socket.emit("unsubscribe", { user_id: user.id });
      }
      socket.disconnect();
      socket = null;
    }
  },

  getSocket() {
    return socket;
  },

  on(event, callback) {
    if (socket) {
      socket.on(event, callback);
    }
  },

  off(event, callback) {
    if (socket) {
      socket.off(event, callback);
    }
  },
};

export default socketService;
