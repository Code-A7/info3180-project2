import api from "./api";

export const profileService = {
  async getProfile() {
    const response = await api.get("/api/profile");
    return response.data;
  },

  async createProfile(profileData) {
    const response = await api.post("/api/profile", profileData);
    return response.data;
  },

  async updateProfile(profileData) {
    const response = await api.put("/api/profile", profileData);
    return response.data;
  },

  async uploadPicture(file) {
    const formData = new FormData();
    formData.append("file", file);

    const response = await api.post("/api/profile/picture", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });
    return response.data;
  },

  async getUserProfile(userId) {
    const response = await api.get(`/api/profile/${userId}`);
    return response.data;
  },
};

export default profileService;
