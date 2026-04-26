<template>
  <div class="conversations-container">
    <div class="conversations-header">
      <h1>Messages</h1>
      <p>Your conversations</p>
    </div>

    <div v-if="loading" class="loading">
      <div class="loading-spinner"></div>
      <p>Loading conversations...</p>
    </div>

    <div v-else-if="conversations.length === 0" class="no-conversations">
      <div class="no-conversations-icon">💬</div>
      <h3>No conversations yet</h3>
      <p>Match with someone to start chatting!</p>
      <router-link to="/browse" class="btn-primary"
        >Browse Profiles</router-link
      >
    </div>

    <div v-else class="conversations-list">
      <div
        v-for="conv in conversations"
        :key="conv.user_id"
        class="conversation-item"
        :class="{ unread: conv.unread_count > 0 }"
        @click="openChat(conv.user_id)"
      >
        <div class="conversation-avatar">
          <img
            v-if="conv.profile_picture"
            :src="`http://localhost:5000/uploads/${conv.profile_picture}`"
            alt="Profile"
          />
          <div v-else class="avatar-placeholder">
            {{ conv.user_name?.charAt(0) }}
          </div>
          <div v-if="conv.unread_count > 0" class="online-indicator"></div>
        </div>

        <div class="conversation-content">
          <div class="conversation-header">
            <h3>{{ conv.user_name }}</h3>
            <span class="time">{{ formatTime(conv.last_message_at) }}</span>
          </div>
          <p class="last-message">
            {{ conv.last_message || "Start a conversation!" }}
          </p>
        </div>

        <div v-if="conv.unread_count > 0" class="unread-badge">
          {{ conv.unread_count > 9 ? "9+" : conv.unread_count }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from "vue";
import { useRouter } from "vue-router";
import messageService from "../services/messageService";
import socketService from "../services/socketService";

const router = useRouter();
const conversations = ref([]);
const loading = ref(true);

const loadConversations = async () => {
  try {
    conversations.value = await messageService.getConversations();
  } catch (error) {
    console.error("Failed to load conversations:", error);
  } finally {
    loading.value = false;
  }
};

const openChat = (userId) => {
  router.push(`/messages/${userId}`);
};

const formatTime = (dateString) => {
  if (!dateString) return "";
  const date = new Date(dateString);
  const now = new Date();
  const diff = now - date;

  if (diff < 60000) return "now";
  if (diff < 3600000) return `${Math.floor(diff / 60000)}m`;
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}h`;
  if (diff < 604800000) return `${Math.floor(diff / 86400000)}d`;
  return date.toLocaleDateString();
};

const handleNewMessage = (data) => {
  loadConversations();
};

onMounted(() => {
  loadConversations();
  socketService.on("new_message", handleNewMessage);
});

onUnmounted(() => {
  socketService.off("new_message", handleNewMessage);
});
</script>

<style scoped>
.conversations-container {
  max-width: 600px;
  margin: 0 auto;
  padding: 1.5rem;
}

.conversations-header {
  text-align: center;
  margin-bottom: 1.5rem;
}

.conversations-header h1 {
  font-size: 2rem;
  font-weight: 700;
  background: linear-gradient(135deg, #14b8a6, #8b5cf6);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 0.5rem;
}

.conversations-header p {
  color: #6b7280;
}

:global(.dark) .conversations-header p {
  color: #9ca3af;
}

.conversations-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.conversation-item {
  display: flex;
  align-items: center;
  padding: 1rem;
  background: rgba(255, 255, 255, 0.6);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(20, 184, 166, 0.1);
  border-radius: 1rem;
  cursor: pointer;
  transition: all 0.2s;
}

:global(.dark) .conversation-item {
  background: rgba(31, 41, 55, 0.6);
  border-color: rgba(139, 92, 246, 0.15);
}

.conversation-item:hover {
  background: rgba(255, 255, 255, 0.9);
  transform: translateX(4px);
  box-shadow: 0 4px 15px rgba(20, 184, 166, 0.1);
}

:global(.dark) .conversation-item:hover {
  background: rgba(55, 65, 81, 0.8);
}

.conversation-item.unread {
  background: rgba(20, 184, 166, 0.08);
  border-color: rgba(20, 184, 166, 0.2);
}

:global(.dark) .conversation-item.unread {
  background: rgba(139, 92, 246, 0.1);
  border-color: rgba(139, 92, 246, 0.3);
}

.conversation-avatar {
  position: relative;
  width: 52px;
  height: 52px;
  border-radius: 50%;
  overflow: hidden;
  margin-right: 1rem;
  flex-shrink: 0;
  border: 2px solid rgba(20, 184, 166, 0.2);
}

.conversation-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar-placeholder {
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #14b8a6, #8b5cf6);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
  font-weight: bold;
}

.online-indicator {
  position: absolute;
  bottom: 2px;
  right: 2px;
  width: 12px;
  height: 12px;
  background: #10b981;
  border: 2px solid white;
  border-radius: 50%;
}

:global(.dark) .online-indicator {
  border-color: #1f2937;
}

.conversation-content {
  flex: 1;
  min-width: 0;
}

.conversation-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.25rem;
}

.conversation-header h3 {
  font-size: 1rem;
  font-weight: 700;
  color: #111827;
  margin: 0;
}

:global(.dark) .conversation-header h3 {
  color: #f9fafb;
}

.time {
  font-size: 0.75rem;
  color: #9ca3af;
  font-weight: 500;
}

.last-message {
  color: #6b7280;
  font-size: 0.85rem;
  margin: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

:global(.dark) .last-message {
  color: #9ca3af;
}

.conversation-item.unread .last-message {
  color: #374151;
  font-weight: 500;
}

:global(.dark) .conversation-item.unread .last-message {
  color: #d1d5db;
}

.unread-badge {
  background: linear-gradient(135deg, #14b8a6, #0d9488);
  color: white;
  border-radius: 50%;
  width: 22px;
  height: 22px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.7rem;
  font-weight: 700;
  margin-left: 0.75rem;
  flex-shrink: 0;
}

.no-conversations {
  text-align: center;
  padding: 4rem 2rem;
  background: rgba(255, 255, 255, 0.5);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(20, 184, 166, 0.1);
  border-radius: 1rem;
}

:global(.dark) .no-conversations {
  background: rgba(31, 41, 55, 0.5);
}

.no-conversations-icon {
  font-size: 3.5rem;
  margin-bottom: 1rem;
}

.no-conversations h3 {
  color: #374151;
  margin-bottom: 0.5rem;
}

:global(.dark) .no-conversations h3 {
  color: #f3f4f6;
}

.no-conversations p {
  color: #6b7280;
  margin-bottom: 1.5rem;
}

:global(.dark) .no-conversations p {
  color: #9ca3af;
}

.btn-primary {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  background: linear-gradient(135deg, #14b8a6, #0d9488);
  color: white;
  border-radius: 0.6rem;
  text-decoration: none;
  font-weight: 600;
  transition: all 0.2s;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(20, 184, 166, 0.4);
}

.loading {
  text-align: center;
  padding: 4rem;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid rgba(20, 184, 166, 0.2);
  border-top-color: #14b8a6;
  border-radius: 50%;
  margin: 0 auto 1rem;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.loading p {
  color: #6b7280;
  font-weight: 500;
}
</style>
