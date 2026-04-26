<template>
  <div class="search-container">
    <div class="search-header">
      <h1>Search Profiles</h1>
      <p>Find your perfect match</p>
    </div>

    <div class="search-form">
      <div class="form-grid">
        <div class="form-group">
          <label>
            <svg
              xmlns="http://www.w3.org/2000/svg"
              class="label-icon"
              viewBox="0 0 20 20"
              fill="currentColor"
            >
              <path d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" />
            </svg>
            Age Range
          </label>
          <div class="age-inputs">
            <input
              v-model.number="searchParams.age_min"
              type="number"
              placeholder="Min"
              min="18"
              max="100"
              class="form-input"
            />
            <span class="age-separator">-</span>
            <input
              v-model.number="searchParams.age_max"
              type="number"
              placeholder="Max"
              min="18"
              max="100"
              class="form-input"
            />
          </div>
        </div>

        <div class="form-group">
          <label>
            <svg
              xmlns="http://www.w3.org/2000/svg"
              class="label-icon"
              viewBox="0 0 20 20"
              fill="currentColor"
            >
              <path
                fill-rule="evenodd"
                d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z"
                clip-rule="evenodd"
              />
            </svg>
            Age Range
          </label>
          <div class="age-inputs">
            <input
              v-model.number="searchParams.age_min"
              type="number"
              placeholder="Min"
              min="18"
              max="100"
              class="form-input"
            />
            <span class="age-separator">-</span>
            <input
              v-model.number="searchParams.age_max"
              type="number"
              placeholder="Max"
              min="18"
              max="100"
              class="form-input"
            />
          </div>
        </div>
      </div>

      <div class="form-grid">
        <div class="form-group">
          <label>
            <svg
              xmlns="http://www.w3.org/2000/svg"
              class="label-icon"
              viewBox="0 0 20 20"
              fill="currentColor"
            >
              <path d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" />
            </svg>
            Gender
          </label>
          <select v-model="searchParams.gender" class="form-select">
            <option value="">Any</option>
            <option value="male">Male</option>
            <option value="female">Female</option>
            <option value="non-binary">Non-binary</option>
          </select>
        </div>

        <div class="form-group">
          <label>
            <svg
              xmlns="http://www.w3.org/2000/svg"
              class="label-icon"
              viewBox="0 0 20 20"
              fill="currentColor"
            >
              <path
                d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"
              />
            </svg>
            Relationship Goal
          </label>
          <select v-model="searchParams.relationship_goal" class="form-select">
            <option value="">Any</option>
            <option value="dating">Dating</option>
            <option value="relationship">Relationship</option>
            <option value="friendship">Friendship</option>
            <option value="casual">Casual</option>
          </select>
        </div>
      </div>

      <div class="form-grid">
        <div class="form-group">
          <label>
            <svg
              xmlns="http://www.w3.org/2000/svg"
              class="label-icon"
              viewBox="0 0 20 20"
              fill="currentColor"
            >
              <path
                d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"
              />
            </svg>
            Interests
          </label>
          <input
            v-model="interestsInput"
            type="text"
            placeholder="music, travel, gaming (comma separated)"
            class="form-input"
          />
        </div>

        <div class="form-group">
          <label>
            <svg
              xmlns="http://www.w3.org/2000/svg"
              class="label-icon"
              viewBox="0 0 20 20"
              fill="currentColor"
            >
              <path
                fill-rule="evenodd"
                d="M6 6V5a3 3 0 013-3h2a3 3 0 013 3v1h2a2 2 0 012 2v3.57A22.952 22.952 0 0110 13a22.95 22.95 0 01-8-1.43V8a2 2 0 012-2h2zm2-1a1 1 0 011-1h2a1 1 0 011 1v1H8V5zm1 5a1 1 0 011-1h.01a1 1 0 110 2H10a1 1 0 01-1-1z"
                clip-rule="evenodd"
              />
              <path
                d="M2 13.692V16a2 2 0 002 2h12a2 2 0 002-2v-2.308A24.974 24.974 0 0110 15c-2.796 0-5.487-.46-8-1.308z"
              />
            </svg>
            Occupation
          </label>
          <input
            v-model="searchParams.occupation"
            type="text"
            placeholder="Job title or field"
            class="form-input"
          />
        </div>
      </div>

      <div class="form-row-single">
        <div class="form-group">
          <label>
            <svg
              xmlns="http://www.w3.org/2000/svg"
              class="label-icon"
              viewBox="0 0 20 20"
              fill="currentColor"
            >
              <path
                d="M3 4a1 1 0 011-1h12a1 1 0 011 1v2a1 1 0 01-1 1H4a1 1 0 01-1-1V4zM3 10a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H4a1 1 0 01-1-1v-6zM14 9a1 1 0 00-1 1v6a1 1 0 001 1h2a1 1 0 001-1v-6a1 1 0 00-1-1h-2z"
              />
            </svg>
            Sort By
          </label>
          <select v-model="searchParams.sort_by" class="form-select">
            <option value="newest">Newest</option>
            <option value="oldest">Oldest</option>
            <option value="similarity">Most Similar</option>
            <option value="age_asc">Age: Youngest first</option>
            <option value="age_desc">Age: Oldest first</option>
          </select>
        </div>
      </div>

      <div class="form-actions">
        <button class="btn-search" :disabled="searching" @click="handleSearch">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            class="btn-icon"
            viewBox="0 0 20 20"
            fill="currentColor"
          >
            <path
              fill-rule="evenodd"
              d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z"
              clip-rule="evenodd"
            />
          </svg>
          {{ searching ? "Searching..." : "Search" }}
        </button>
        <button class="btn-clear" @click="clearFilters">Clear Filters</button>
      </div>
    </div>

    <div v-if="loading" class="loading">
      <div class="loading-spinner"></div>
      <p>Finding matches...</p>
    </div>

    <div v-else-if="results.length === 0 && searched" class="no-results">
      <div class="no-results-icon">🔍</div>
      <h3>No profiles found</h3>
      <p>Try adjusting your search criteria</p>
    </div>

    <div v-else class="results-grid">
      <div
        v-for="profile in results"
        :key="profile.user_id"
        class="profile-card"
      >
        <div class="profile-image">
          <img
            v-if="profile.profile_picture"
            :src="`http://localhost:5000/uploads/${profile.profile_picture}`"
            alt="Profile"
          />
          <div v-else class="avatar-placeholder">
            {{ profile.name?.charAt(0) }}
          </div>
          <div v-if="profile.match_score" class="match-badge">
            {{ profile.match_score }}%
          </div>
        </div>

        <div class="profile-info">
          <h3>{{ profile.name }}, {{ profile.age }}</h3>

          <p class="bio">
            {{ profile.bio?.substring(0, 80)
            }}{{ profile.bio?.length > 80 ? "..." : "" }}
          </p>

          <div class="interests">
            <span
              v-for="interest in profile.interests?.slice(0, 3)"
              :key="interest"
              class="interest-tag"
            >
              {{ interest }}
            </span>
          </div>

          <div class="profile-actions">
            <button
              class="btn-bookmark"
              :class="{ active: profile.is_bookmarked }"
              @click="toggleBookmark(profile)"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                class="bookmark-icon"
                viewBox="0 0 20 20"
                fill="currentColor"
              >
                <path d="M5 4a2 2 0 012-2h6a2 2 0 012 2v14l-5-2.5L5 18V4z" />
              </svg>
            </button>
            <router-link :to="`/profile/${profile.user_id}`" class="btn-view"
              >View Profile</router-link
            >
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from "vue";
import searchService from "../services/searchService";

const searchParams = reactive({
  age_min: null,
  age_max: null,
  gender: "",
  relationship_goal: "",
  occupation: "",
  sort_by: "newest",
});

const interestsInput = ref("");
const results = ref([]);
const loading = ref(false);
const searching = ref(false);
const searched = ref(false);

const handleSearch = async () => {
  loading.value = true;
  searching.value = true;
  searched.value = true;

  try {
    const params = { ...searchParams };

    if (interestsInput.value) {
      params.interests = interestsInput.value
        .split(",")
        .map((i) => i.trim())
        .filter((i) => i);
    }

    Object.keys(params).forEach((key) => {
      if (params[key] === "" || params[key] === null) {
        delete params[key];
      }
    });

    results.value = await searchService.searchProfiles(params);
  } catch (error) {
    console.error("Search failed:", error);
  } finally {
    loading.value = false;
    searching.value = false;
  }
};

const clearFilters = () => {
  searchParams.age_min = null;
  searchParams.age_max = null;
  searchParams.gender = "";
  searchParams.relationship_goal = "";
  searchParams.occupation = "";
  searchParams.sort_by = "newest";
  interestsInput.value = "";
  results.value = [];
  searched.value = false;
};

const toggleBookmark = async (profile) => {
  try {
    await searchService.toggleBookmark(profile.user_id, profile.is_bookmarked);
    profile.is_bookmarked = !profile.is_bookmarked;
  } catch (error) {
    console.error("Failed to toggle bookmark:", error);
  }
};
</script>

<style scoped>
.search-container {
  max-width: 900px;
  margin: 0 auto;
  padding: 1.5rem;
}

.search-header {
  text-align: center;
  margin-bottom: 2rem;
}

.search-header h1 {
  font-size: 2rem;
  font-weight: 700;
  background: linear-gradient(135deg, #14b8a6, #8b5cf6);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 0.5rem;
}

.search-header p {
  color: #6b7280;
}

:global(.dark) .search-header p {
  color: #9ca3af;
}

.search-form {
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(20, 184, 166, 0.15);
  padding: 1.5rem;
  border-radius: 1rem;
  margin-bottom: 2rem;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
}

:global(.dark) .search-form {
  background: rgba(31, 41, 55, 0.7);
  border-color: rgba(139, 92, 246, 0.2);
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1.25rem;
  margin-bottom: 1.25rem;
}

.form-row-single {
  margin-bottom: 1.25rem;
}

.form-row-single .form-group {
  max-width: 300px;
}

.form-group {
  display: flex;
  flex-direction: column;
}

.form-group label {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  font-weight: 600;
  font-size: 0.85rem;
  color: #374151;
  margin-bottom: 0.5rem;
}

:global(.dark) .form-group label {
  color: #d1d5db;
}

.label-icon {
  width: 16px;
  height: 16px;
  color: #14b8a6;
}

.form-input,
.form-select {
  padding: 0.7rem 0.9rem;
  border: 1px solid rgba(20, 184, 166, 0.25);
  border-radius: 0.6rem;
  font-size: 0.9rem;
  background: rgba(255, 255, 255, 0.8);
  color: #1f2937;
  transition: all 0.2s;
}

:global(.dark) .form-input,
:global(.dark) .form-select {
  background: rgba(55, 65, 81, 0.8);
  border-color: rgba(139, 92, 246, 0.3);
  color: #f3f4f6;
}

.form-input:focus,
.form-select:focus {
  outline: none;
  border-color: #14b8a6;
  box-shadow: 0 0 0 3px rgba(20, 184, 166, 0.15);
}

.age-inputs {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.age-inputs .form-input {
  width: 80px;
}

.age-separator {
  color: #9ca3af;
  font-weight: 600;
}

.form-actions {
  display: flex;
  gap: 1rem;
  margin-top: 1.5rem;
}

.btn-search {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.8rem 1.5rem;
  background: linear-gradient(135deg, #14b8a6, #0d9488);
  color: white;
  border: none;
  border-radius: 0.6rem;
  font-weight: 600;
  font-size: 0.95rem;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-search:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(20, 184, 166, 0.4);
}

.btn-search:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-icon {
  width: 18px;
  height: 18px;
}

.btn-clear {
  padding: 0.8rem 1.5rem;
  background: rgba(107, 114, 128, 0.1);
  color: #6b7280;
  border: 1px solid rgba(107, 114, 128, 0.2);
  border-radius: 0.6rem;
  font-weight: 600;
  font-size: 0.95rem;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-clear:hover {
  background: rgba(107, 114, 128, 0.2);
  color: #374151;
}

.results-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 1.5rem;
}

.profile-card {
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(20, 184, 166, 0.1);
  border-radius: 1rem;
  overflow: hidden;
  transition: all 0.3s;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
}

:global(.dark) .profile-card {
  background: rgba(31, 41, 55, 0.8);
  border-color: rgba(139, 92, 246, 0.15);
}

.profile-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 30px rgba(20, 184, 166, 0.15);
}

.profile-image {
  position: relative;
  height: 180px;
  overflow: hidden;
}

.profile-image img {
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
  font-size: 3rem;
  font-weight: bold;
}

.match-badge {
  position: absolute;
  top: 0.75rem;
  right: 0.75rem;
  padding: 0.25rem 0.6rem;
  background: linear-gradient(135deg, #10b981, #059669);
  color: white;
  border-radius: 9999px;
  font-size: 0.7rem;
  font-weight: 700;
}

.profile-info {
  padding: 1rem;
}

.profile-info h3 {
  font-size: 1.1rem;
  font-weight: 700;
  color: #111827;
  margin: 0 0 0.25rem;
}

:global(.dark) .profile-info h3 {
  color: #f9fafb;
}

.bio {
  font-size: 0.8rem;
  color: #6b7280;
  margin: 0 0 0.75rem;
  line-height: 1.4;
}

:global(.dark) .bio {
  color: #9ca3af;
}

.interests {
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
  margin-bottom: 0.75rem;
}

.interest-tag {
  padding: 0.2rem 0.5rem;
  background: linear-gradient(
    135deg,
    rgba(20, 184, 166, 0.12),
    rgba(139, 92, 246, 0.12)
  );
  color: #4b5563;
  border-radius: 9999px;
  font-size: 0.65rem;
  font-weight: 600;
  border: 1px solid rgba(20, 184, 166, 0.15);
}

:global(.dark) .interest-tag {
  background: linear-gradient(
    135deg,
    rgba(20, 184, 166, 0.2),
    rgba(139, 92, 246, 0.2)
  );
  color: #d1d5db;
}

.profile-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 0.75rem;
  border-top: 1px solid rgba(229, 231, 235, 0.5);
}

:global(.dark) .profile-actions {
  border-color: rgba(55, 65, 81, 0.5);
}

.btn-bookmark {
  background: none;
  border: 1px solid rgba(107, 114, 128, 0.3);
  border-radius: 0.5rem;
  padding: 0.4rem;
  cursor: pointer;
  color: #9ca3af;
  transition: all 0.2s;
}

.btn-bookmark:hover {
  border-color: #14b8a6;
  color: #14b8a6;
}

.btn-bookmark.active {
  background: linear-gradient(135deg, #14b8a6, #0d9488);
  border-color: #14b8a6;
  color: white;
}

.bookmark-icon {
  width: 18px;
  height: 18px;
}

.btn-view {
  padding: 0.5rem 1rem;
  background: linear-gradient(135deg, #8b5cf6, #7c3aed);
  color: white;
  border-radius: 0.5rem;
  text-decoration: none;
  font-size: 0.8rem;
  font-weight: 600;
  transition: all 0.2s;
}

.btn-view:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 15px rgba(139, 92, 246, 0.4);
}

.no-results {
  text-align: center;
  padding: 3rem;
}

.no-results-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.no-results h3 {
  color: #374151;
  margin-bottom: 0.5rem;
}

:global(.dark) .no-results h3 {
  color: #f3f4f6;
}

.no-results p {
  color: #6b7280;
}

.loading {
  text-align: center;
  padding: 3rem;
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
