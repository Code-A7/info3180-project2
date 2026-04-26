import api from "./api";

export const searchService = {
  async searchProfiles(params) {
    const response = await api.post("/api/matches/search", params);
    return response.data;
  },

  async getBookmarks() {
    const response = await api.get("/api/matches/bookmarks");
    return response.data;
  },

  async addBookmark(userId) {
    const response = await api.post(`/api/matches/bookmark/${userId}`);
    return response.data;
  },

  async removeBookmark(userId) {
    const response = await api.delete(`/api/matches/bookmark/${userId}`);
    return response.data;
  },

  async toggleBookmark(userId, isBookmarked) {
    if (isBookmarked) {
      return this.removeBookmark(userId);
    } else {
      return this.addBookmark(userId);
    }
  },
};

export default searchService;
