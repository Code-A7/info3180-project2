<template>
  <div class="matches-container">
    <h1>Your Matches</h1>

    <div v-if="loading" class="loading">Loading matches...</div>

    <div v-else-if="matches.length === 0" class="no-matches">
      <h3>No matches yet</h3>
      <p>Start browsing to find your perfect match!</p>
      <router-link to="/browse" class="btn-primary">Browse Profiles</router-link>
    </div>

    <div v-else class="matches-grid">
      <div v-for="match in matches" :key="match.match_id" class="match-card">
        <div class="match-image" @click="viewProfile(match.profile.user_id)">
          <img
            v-if="match.profile.profile_picture"
            :src="`http://localhost:5000/uploads/${match.profile.profile_picture}`"
            alt="Profile"
          />
          <div v-else class="avatar-placeholder">
            {{ match.profile.name?.charAt(0) }}
          </div>
        </div>

        <div class="match-info">
          <h3>{{ match.profile.name }}, {{ match.profile.age }}</h3>
          <p class="matched-at">Matched {{ formatDate(match.matched_at) }}</p>

          <div class="match-actions">
            <button class="btn-message" @click="goToMessage(match.profile.user_id)">
              💬 Message
            </button>
            <button class="btn-profile" @click="viewProfile(match.profile.user_id)">
              View Profile
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import matchService from "../services/matchService";

const matches = ref([]);
const loading = ref(true);
const router = useRouter();

const loadMatches = async () => {
  loading.value = true;
  try {
    matches.value = await matchService.getMatches();
  } catch (error) {
    console.error("Failed to load matches:", error);
  } finally {
    loading.value = false;
  }
};

const goToMessage = (userId) => {
  router.push(`/messages/${userId}`);
};

const viewProfile = (userId) => {
  router.push(`/profile/${userId}`);
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

onMounted(loadMatches);
</script>

<style scoped>
.matches-container {
  max-width: 900px;
  margin: 0 auto;
  padding: 1.5rem;
}

h1 {
  font-size: 1.75rem;
  font-weight: 700;
  background: linear-gradient(135deg, #14b8a6, #8b5cf6);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 1.5rem;
}

.loading {
  text-align: center;
  padding: 3.75rem;
  color: #6b7280;
}

.no-matches {
  text-align: center;
  padding: 3.75rem;
  background: white;
  border-radius: 1rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.no-matches h3 {
  color: #111827;
  margin-bottom: 0.5rem;
}

.no-matches p {
  color: #6b7280;
  margin-bottom: 1.25rem;
}

.btn-primary {
  display: inline-block;
  padding: 0.875rem 1.875rem;
  background: linear-gradient(to right, #14b8a6, #0d9488);
  color: white;
  text-decoration: none;
  border-radius: 0.5rem;
  font-weight: 600;
  transition: all 0.2s;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(20, 184, 166, 0.3);
}

.matches-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 1.25rem;
}

.match-card {
  background: white;
  border-radius: 1rem;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  transition: all 0.3s;
}

.match-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

.match-image {
  width: 100%;
  height: 200px;
  background: linear-gradient(135deg, #f3f4f6, #e5e7eb);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  overflow: hidden;
}

.match-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar-placeholder {
  font-size: 60px;
  color: #e91e63;
  font-weight: bold;
}

.match-info {
  padding: 15px;
}

.match-info h3 {
  margin: 0 0 4px 0;
  color: #111827;
  font-size: 1rem;
  font-weight: 600;
}

.matched-at {
  font-size: 12px;
  color: #9ca3af;
  margin: 0 0 12px 0;
}

.match-actions {
  display: flex;
  gap: 8px;
}

.btn-message {
  flex: 1;
  padding: 8px 12px;
  background: linear-gradient(to right, #14b8a6, #0d9488);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-message:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 10px rgba(20, 184, 166, 0.35);
}

.btn-profile {
  flex: 1;
  padding: 8px 12px;
  background: transparent;
  color: #6b7280;
  border: 1.5px solid #e5e7eb;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-profile:hover {
  border-color: #14b8a6;
  color: #14b8a6;
}
</style>
