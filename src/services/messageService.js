import api from "./api";

export const messageService = {
  async getConversations() {
    const response = await api.get("/api/messages");
    return response.data;
  },

  async getMessageHistory(otherUserId, page = 1, perPage = 50) {
    const response = await api.get(`/api/messages/${otherUserId}`, {
      params: { page, per_page: perPage },
    });
    return response.data;
  },

  async sendMessage(otherUserId, content) {
    const response = await api.post(`/api/messages/${otherUserId}`, {
      content,
    });
    return response.data;
  },

  async markMessageRead(messageId) {
    const response = await api.put(`/api/messages/${messageId}/read`);
    return response.data;
  },

  async getUnreadCount() {
    const response = await api.get("/api/messages/unread");
    return response.data;
  },

  async sendTypingStatus(otherUserId, isTyping) {
    const response = await api.post(`/api/messages/typing/${otherUserId}`, {
      is_typing: isTyping,
    });
    return response.data;
  },
};

export default messageService;
