<template>
  <div class="profile-container">
    <div v-if="loading" class="loading">Loading...</div>

    <div v-else-if="!hasProfile && isOwnProfile" class="no-profile">
      <h2>Create Your Profile</h2>
      <p>You haven't created a profile yet. Let's get started!</p>
      <router-link to="/profile/edit" class="btn-primary"
        >Create Profile</router-link
      >
    </div>

    <div v-else-if="!profile" class="no-profile">
      <h2>Profile Not Found</h2>
      <p>This profile doesn't exist or is no longer available.</p>
      <router-link to="/browse" class="btn-primary"
        >Browse Profiles</router-link
      >
    </div>

    <div v-else class="profile-card">
      <div class="profile-header">
        <div class="avatar" :class="{ 'has-preview': previewUrl }">
          <img
            v-if="profile.profile_picture || previewUrl"
            :src="
              previewUrl ||
              `http://localhost:5000/uploads/${profile.profile_picture}?t=${avatarTimestamp}`
            "
            alt="Profile Picture"
          />
          <div v-else class="avatar-placeholder">
            {{ profile.name?.charAt(0) }}
          </div>

          <Transition name="fade">
            <div v-if="uploading" class="avatar-overlay">
              <div class="upload-spinner"></div>
            </div>
          </Transition>
        </div>
        <div class="profile-info">
          <h2>{{ profile.name }}</h2>
          <p class="age-location">{{ profile.age }} years old</p>
          <span
            v-if="isOwnProfile"
            class="visibility-badge"
            :class="{ private: !profile.visibility }"
          >
            {{ profile.visibility ? "Public" : "Private" }}
          </span>
        </div>
        <div class="profile-actions-header">
          <router-link v-if="isOwnProfile" to="/profile/edit" class="btn-edit"
            >Edit Profile</router-link
          >
          <router-link v-else :to="`/messages/${userId}`" class="btn-message"
            >Send Message</router-link
          >
        </div>
      </div>

      <div class="profile-section">
        <h3>About Me</h3>
        <p>{{ profile.bio || "No bio added yet." }}</p>
      </div>

      <div class="profile-section">
        <h3>Interests</h3>
        <div class="interests">
          <span
            v-for="interest in profile.interests"
            :key="interest"
            class="interest-tag"
          >
            {{ interest }}
          </span>
        </div>
      </div>

      <div class="profile-details">
        <div class="detail-item">
          <strong>Gender:</strong> {{ formatGenderPreference(profile.gender) }}
        </div>
        <div class="detail-item">
          <strong>Interested In:</strong>
          {{ formatGenderPreference(profile.gender_preference) }}
        </div>
        <div class="detail-item">
          <strong>Relationship Goal:</strong>
          {{ formatRelationshipGoal(profile.relationship_goal) }}
        </div>
        <div class="detail-item">
          <strong>Occupation:</strong>
          {{ profile.occupation || "Not specified" }}
        </div>
      </div>

      <div v-if="isOwnProfile" class="profile-actions">
        <label class="upload-btn" :class="{ 'is-uploading': uploading }">
          <input
            type="file"
            accept="image/jpeg,image/png,image/gif,image/webp"
            :disabled="uploading"
            @change="handlePictureUpload"
          />
          <svg
            v-if="!uploading"
            xmlns="http://www.w3.org/2000/svg"
            class="upload-icon"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
          >
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
            <polyline points="17 8 12 3 7 8" />
            <line x1="12" y1="3" x2="12" y2="15" />
          </svg>
          <svg
            v-else
            class="upload-icon spinning"
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
          >
            <path d="M21 12a9 9 0 1 1-6.219-8.56" />
          </svg>
          <span v-if="uploading">Uploading...</span>
          <span v-else>Upload New Photo</span>
        </label>
        <p class="upload-hint">JPG, PNG, GIF, or WebP (max 5MB)</p>
      </div>
    </div>

    <!-- Toast Notifications -->
    <Teleport to="body">
      <TransitionGroup name="toast" tag="div" class="toast-container">
        <div
          v-for="toast in toasts"
          :key="toast.id"
          class="toast"
          :class="toast.type"
        >
          <div class="toast-icon">
            <svg
              v-if="toast.type === 'success'"
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
            >
              <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
              <polyline points="22 4 12 14.01 9 11.01" />
            </svg>
            <svg
              v-else-if="toast.type === 'error'"
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
            >
              <circle cx="12" cy="12" r="10" />
              <line x1="15" y1="9" x2="9" y2="15" />
              <line x1="9" y1="9" x2="15" y2="15" />
            </svg>
            <svg
              v-else
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
            >
              <circle cx="12" cy="12" r="10" />
              <line x1="12" y1="8" x2="12" y2="12" />
              <line x1="12" y1="16" x2="12.01" y2="16" />
            </svg>
          </div>
          <div class="toast-content">
            <p class="toast-title">{{ toast.title }}</p>
            <p class="toast-message">{{ toast.message }}</p>
          </div>
          <button class="toast-close" @click="removeToast(toast.id)">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
            >
              <line x1="18" y1="6" x2="6" y2="18" />
              <line x1="6" y1="6" x2="18" y2="18" />
            </svg>
          </button>
        </div>
      </TransitionGroup>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { useRoute } from "vue-router";
import profileService from "../services/profileService";
import authService from "../services/authService";

const route = useRoute();
const loading = ref(true);
const hasProfile = ref(false);
const profile = ref(null);
const uploading = ref(false);
const avatarTimestamp = ref(Date.now());
const previewUrl = ref(null);
const toasts = ref([]);
let toastId = 0;

const userId = computed(() => route.params.userId);
const isOwnProfile = computed(() => !userId.value);

const formatGenderPreference = (pref) => {
  const map = {
    all: "Everyone",
    male: "Men",
    female: "Women",
    non_binary: "Non-Binary",
    prefer_not_to_say: "Prefer not to say",
  };
  return map[pref] || pref || "Not specified";
};

const formatRelationshipGoal = (goal) => {
  const map = {
    friendship: "Friendship",
    casual_dating: "Casual Dating",
    serious_relationship: "Serious Relationship",
    marriage: "Marriage",
  };
  return map[goal] || goal || "Not specified";
};

const loadProfile = async () => {
  loading.value = true;
  try {
    const user = await authService.getCurrentUser();
    if (!user.id) {
      hasProfile.value = false;
      profile.value = null;
      return;
    }

    if (isOwnProfile.value) {
      try {
        const data = await profileService.getProfile();
        profile.value = data;
        hasProfile.value = true;
      } catch (error) {
        if (error.response?.status === 404) {
          hasProfile.value = false;
          profile.value = null;
        } else {
          throw error;
        }
      }
    } else {
      const data = await profileService.getOtherProfile(userId.value);
      profile.value = data;
      hasProfile.value = true;
    }
  } catch (error) {
    console.error("Failed to load profile:", error);
    hasProfile.value = false;
    profile.value = null;
  } finally {
    loading.value = false;
  }
};

const addToast = (type, title, message) => {
  const id = ++toastId;
  toasts.value.push({ id, type, title, message });

  setTimeout(() => {
    removeToast(id);
  }, 4000);
};

const removeToast = (id) => {
  const index = toasts.value.findIndex((t) => t.id === id);
  if (index > -1) {
    toasts.value.splice(index, 1);
  }
};

const validateFile = (file) => {
  const validTypes = ["image/jpeg", "image/png", "image/gif", "image/webp"];
  const maxSize = 5 * 1024 * 1024; // 5MB

  if (!validTypes.includes(file.type)) {
    return {
      valid: false,
      error: "Please select a valid image file (JPG, PNG, GIF, or WebP)",
    };
  }

  if (file.size > maxSize) {
    return {
      valid: false,
      error: "Image is too large. Please select an image smaller than 5MB.",
    };
  }

  return { valid: true };
};

const handlePictureUpload = async (event) => {
  const file = event.target.files[0];
  if (!file) return;

  // Validate file
  const validation = validateFile(file);
  if (!validation.valid) {
    addToast("error", "Upload Failed", validation.error);
    event.target.value = "";
    return;
  }

  // Create preview URL
  previewUrl.value = URL.createObjectURL(file);

  uploading.value = true;

  try {
    await profileService.uploadPicture(file);

    // Update timestamp to force image refresh
    avatarTimestamp.value = Date.now();
    previewUrl.value = null;

    // Reload profile to get updated data
    await loadProfile();

    addToast(
      "success",
      "Profile Picture Updated!",
      "Your new photo has been uploaded successfully.",
    );
  } catch (error) {
    previewUrl.value = null;
    const errorMsg =
      error.response?.data?.error ||
      "Failed to upload picture. Please try again.";
    addToast("error", "Upload Failed", errorMsg);
  } finally {
    uploading.value = false;
    event.target.value = "";
  }
};

// Cleanup preview URL on unmount
import { onUnmounted } from "vue";
onUnmounted(() => {
  if (previewUrl.value) {
    URL.revokeObjectURL(previewUrl.value);
  }
});

onMounted(loadProfile);
</script>

<style scoped>
.profile-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 40px 20px;
}

.loading {
  text-align: center;
  padding: 60px;
  color: #666;
}

.no-profile {
  text-align: center;
  padding: 60px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.no-profile h2 {
  color: #e91e63;
  margin-bottom: 10px;
}

.btn-primary {
  display: inline-block;
  margin-top: 20px;
  padding: 14px 30px;
  background: #e91e63;
  color: white;
  text-decoration: none;
  border-radius: 6px;
  font-weight: 600;
}

.profile-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.profile-header {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 30px;
  background: linear-gradient(135deg, #e91e63 0%, #f48fb1 100%);
  color: white;
}

.avatar {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  overflow: hidden;
  border: 4px solid white;
  flex-shrink: 0;
  position: relative;
}

.avatar.has-preview {
  border-color: #10b981;
  box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.3);
}

.avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: white;
  color: #e91e63;
  font-size: 40px;
  font-weight: bold;
}

.avatar-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
}

.upload-spinner {
  width: 30px;
  height: 30px;
  border: 3px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.profile-info {
  flex: 1;
}

.profile-info h2 {
  margin: 0 0 5px 0;
}

.age-location {
  margin: 0;
  opacity: 0.9;
}

.visibility-badge {
  display: inline-block;
  padding: 4px 12px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 20px;
  font-size: 12px;
  margin-top: 8px;
}

.visibility-badge.private {
  background: rgba(0, 0, 0, 0.2);
}

.profile-actions-header {
  display: flex;
  gap: 0.5rem;
}

.btn-message {
  padding: 10px 20px;
  background: white;
  color: #e91e63;
  text-decoration: none;
  border-radius: 6px;
  font-weight: 600;
  transition: background 0.3s;
}

.btn-message:hover {
  background: #f5f5f5;
}

.btn-edit {
  padding: 10px 20px;
  background: white;
  color: #e91e63;
  text-decoration: none;
  border-radius: 6px;
  font-weight: 600;
  transition: background 0.3s;
}

.btn-edit:hover {
  background: #f5f5f5;
}

.profile-section {
  padding: 25px 30px;
  border-bottom: 1px solid #eee;
}

.profile-section h3 {
  margin: 0 0 12px 0;
  color: #333;
  font-size: 16px;
}

.profile-section p {
  margin: 0;
  color: #666;
  line-height: 1.6;
}

.interests {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.interest-tag {
  padding: 6px 14px;
  background: #fce4ec;
  color: #e91e63;
  border-radius: 20px;
  font-size: 14px;
}

.profile-details {
  padding: 25px 30px;
}

.detail-item {
  margin-bottom: 12px;
  color: #555;
}

.detail-item strong {
  color: #333;
}

.profile-actions {
  padding: 20px 30px;
  border-top: 1px solid #eee;
}

.upload-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: white;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(16, 185, 129, 0.3);
}

.upload-btn:hover:not(.is-uploading) {
  background: linear-gradient(135deg, #059669 0%, #047857 100%);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.4);
}

.upload-btn.is-uploading {
  opacity: 0.8;
  cursor: not-allowed;
  background: linear-gradient(135deg, #6b7280 0%, #4b5563 100%);
  box-shadow: none;
}

.upload-btn input {
  display: none;
}

.upload-icon {
  width: 18px;
  height: 18px;
  flex-shrink: 0;
}

.upload-icon.spinning {
  animation: spin 1s linear infinite;
}

.upload-hint {
  margin: 8px 0 0;
  font-size: 12px;
  color: #9ca3af;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>

<!-- Toast styles (unscoped to work with Teleport) -->
<style>
.toast-container {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 9999;
  display: flex;
  flex-direction: column;
  gap: 12px;
  max-width: 400px;
}

.toast {
  display: flex;
  align-items: flex-start;
  gap: 14px;
  padding: 16px 18px;
  background: white;
  border-radius: 12px;
  box-shadow:
    0 10px 40px rgba(0, 0, 0, 0.15),
    0 4px 12px rgba(0, 0, 0, 0.1);
  border-left: 4px solid #6b7280;
}

.toast.success {
  border-left-color: #10b981;
}

.toast.error {
  border-left-color: #ef4444;
}

.toast.warning {
  border-left-color: #f59e0b;
}

.toast-icon {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.toast.success .toast-icon {
  background: #d1fae5;
  color: #10b981;
}

.toast.error .toast-icon {
  background: #fee2e2;
  color: #ef4444;
}

.toast.warning .toast-icon {
  background: #fef3c7;
  color: #f59e0b;
}

.toast-icon svg {
  width: 16px;
  height: 16px;
}

.toast-content {
  flex: 1;
  min-width: 0;
}

.toast-title {
  font-weight: 600;
  color: #111827;
  margin: 0 0 4px 0;
  font-size: 14px;
  line-height: 1.4;
}

.toast-message {
  color: #6b7280;
  margin: 0;
  font-size: 13px;
  line-height: 1.5;
}

.toast-close {
  background: none;
  border: none;
  padding: 4px;
  cursor: pointer;
  color: #9ca3af;
  transition: color 0.2s;
  flex-shrink: 0;
  border-radius: 4px;
}

.toast-close:hover {
  color: #6b7280;
  background: #f3f4f6;
}

.toast-close svg {
  width: 16px;
  height: 16px;
  display: block;
}

/* Toast animations */
.toast-enter-active {
  animation: slideIn 0.35s cubic-bezier(0.21, 1.02, 0.73, 1);
}

.toast-leave-active {
  animation: slideOut 0.25s ease forwards;
}

.toast-move {
  transition: transform 0.3s ease;
}

@keyframes slideIn {
  from {
    transform: translateX(120%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

@keyframes slideOut {
  from {
    transform: translateX(0);
    opacity: 1;
  }
  to {
    transform: translateX(120%);
    opacity: 0;
  }
}

@media (max-width: 480px) {
  .toast-container {
    left: 16px;
    right: 16px;
    top: auto;
    bottom: 20px;
    max-width: none;
  }

  .toast-enter-active {
    animation: slideUp 0.35s cubic-bezier(0.21, 1.02, 0.73, 1);
  }

  .toast-leave-active {
    animation: slideDown 0.25s ease forwards;
  }

  @keyframes slideUp {
    from {
      transform: translateY(100%);
      opacity: 0;
    }
    to {
      transform: translateY(0);
      opacity: 1;
    }
  }

  @keyframes slideDown {
    from {
      transform: translateY(0);
      opacity: 1;
    }
    to {
      transform: translateY(100%);
      opacity: 0;
    }
  }
}
</style>
