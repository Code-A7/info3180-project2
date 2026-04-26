import api from "./api";

export const matchService = {
  async getPotentialMatches(filters = {}) {
    const params = new URLSearchParams(filters).toString();
    const response = await api.get(`/api/matches/potential?${params}`);
    return response.data;
  },

  async getMatches() {
    const response = await api.get("/api/matches");
    return response.data;
  },

  async likeUser(userId) {
    const response = await api.post(`/api/matches/like/${userId}`);
    return response.data;
  },

  async dislikeUser(userId) {
    const response = await api.post(`/api/matches/dislike/${userId}`);
    return response.data;
  },

  async passUser(userId) {
    const response = await api.post(`/api/matches/pass/${userId}`);
    return response.data;
  },

  async getMatchScore(userId) {
    const response = await api.get(`/api/matches/score/${userId}`);
    return response.data;
  },
};

export default matchService;
