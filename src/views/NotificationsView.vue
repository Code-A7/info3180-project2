<template>
  <div class="notifications-container">
    <div class="header">
      <h1>Notifications</h1>
      <button
        v-if="notifications.length > 0"
        class="mark-all-btn"
        @click="markAllAsRead"
      >
        Mark all as read
      </button>
    </div>

    <div v-if="loading" class="loading">Loading notifications...</div>

    <div v-else-if="notifications.length === 0" class="no-notifications">
      <h3>No notifications yet</h3>
      <p>When someone likes you or matches with you, you'll see it here!</p>
    </div>

    <div v-else class="notifications-list">
      <div
        v-for="notification in notifications"
        :key="notification.id"
        class="notification-item"
        :class="{ unread: !notification.is_read }"
        @click="handleNotificationClick(notification)"
      >
        <div class="notification-icon">
          <span v-if="notification.type === 'match'">💕</span>
          <span v-else-if="notification.type === 'like'">❤️</span>
          <span v-else>🔔</span>
        </div>

        <div class="notification-content">
          <p class="notification-message">{{ notification.message }}</p>
          <p class="notification-time">
            {{ formatDate(notification.created_at) }}
          </p>
        </div>

        <div v-if="!notification.is_read" class="unread-dot"></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from "vue";
import { useRouter } from "vue-router";
import notificationService from "../services/notificationService";
import socketService from "../services/socketService";

const router = useRouter();
const notifications = ref([]);
const loading = ref(true);

const loadNotifications = async () => {
  loading.value = true;
  try {
    notifications.value = await notificationService.getNotifications();
  } catch (error) {
    console.error("Failed to load notifications:", error);
  } finally {
    loading.value = false;
  }
};

const markAllAsRead = async () => {
  try {
    await notificationService.markAllAsRead();
    notifications.value = notifications.value.map((n) => ({
      ...n,
      is_read: true,
    }));
  } catch (error) {
    console.error("Failed to mark all as read:", error);
  }
};

const handleNotificationClick = async (notification) => {
  if (!notification.is_read) {
    try {
      await notificationService.markAsRead(notification.id);
      notification.is_read = true;
    } catch (error) {
      console.error("Failed to mark as read:", error);
    }
  }

  // Navigate based on notification type
  if (notification.type === "match" || notification.type === "like") {
    router.push("/matches");
  }
};

const formatDate = (dateString) => {
  if (!dateString) return "";
  const date = new Date(dateString);
  const now = new Date();
  const diff = now - date;

  if (diff < 60000) return "just now";
  if (diff < 3600000) return `${Math.floor(diff / 60000)} minutes ago`;
  if (diff < 86400000) return `${Math.floor(diff / 3600000)} hours ago`;
  if (diff < 604800000) return `${Math.floor(diff / 86400000)} days ago`;
  return date.toLocaleDateString();
};

const handleNewNotification = (notification) => {
  notifications.value.unshift(notification);
};

onMounted(() => {
  loadNotifications();
  socketService.on("notification", handleNewNotification);
  socketService.on("new_match", handleNewNotification);
  socketService.on("new_like", handleNewNotification);
});

onUnmounted(() => {
  socketService.off("notification", handleNewNotification);
  socketService.off("new_match", handleNewNotification);
  socketService.off("new_like", handleNewNotification);
});
</script>

<style scoped>
.notifications-container {
  max-width: 600px;
  margin: 0 auto;
  padding: 20px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

h1 {
  color: #e91e63;
  margin: 0;
}

.mark-all-btn {
  padding: 8px 16px;
  background: #f5f5f5;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  color: #666;
}

.mark-all-btn:hover {
  background: #eee;
}

.loading {
  text-align: center;
  padding: 60px;
  color: #666;
}

.no-notifications {
  text-align: center;
  padding: 60px;
  background: white;
  border-radius: 12px;
}

.no-notifications h3 {
  color: #333;
  margin-bottom: 10px;
}

.no-notifications p {
  color: #666;
}

.notifications-list {
  background: white;
  border-radius: 12px;
  overflow: hidden;
}

.notification-item {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 15px 20px;
  border-bottom: 1px solid #eee;
  cursor: pointer;
  transition: background 0.2s;
}

.notification-item:hover {
  background: #f9f9f9;
}

.notification-item.unread {
  background: #fce4ec;
}

.notification-icon {
  font-size: 24px;
}

.notification-content {
  flex: 1;
}

.notification-message {
  margin: 0 0 5px 0;
  color: #333;
}

.notification-time {
  margin: 0;
  font-size: 12px;
  color: #999;
}

.unread-dot {
  width: 10px;
  height: 10px;
  background: #e91e63;
  border-radius: 50%;
}
</style>
