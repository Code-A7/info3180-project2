<template>
  <div class="edit-container">
    <div class="edit-card">
      <h2>{{ isEdit ? "Edit Profile" : "Create Profile" }}</h2>

      <form @submit.prevent="handleSubmit">
        <div class="form-row">
          <div class="form-group">
            <label for="name">Name *</label>
            <input id="name" v-model="form.name" type="text" required />
            <span v-if="errors.name" class="error">{{ errors.name[0] }}</span>
          </div>

          <div class="form-group">
            <label for="age">Age *</label>
            <input
              id="age"
              v-model.number="form.age"
              type="number"
              min="18"
              max="120"
              required
            />
            <span v-if="errors.age" class="error">{{ errors.age[0] }}</span>
          </div>
        </div>

        <div class="form-group">
          <label for="bio">About Me</label>
          <textarea
            id="bio"
            v-model="form.bio"
            rows="4"
            placeholder="Tell us about yourself..."
          ></textarea>
        </div>

        <div class="form-group">
          <label for="interests"
            >Interests (minimum 3, comma separated) *</label
          >
          <input
            id="interests"
            v-model="form.interests"
            type="text"
            placeholder="e.g., Reading, Hiking, Cooking, Music"
            required
          />
          <span v-if="errors.interests" class="error">{{
            errors.interests[0]
          }}</span>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label for="gender">Gender</label>
            <select id="gender" v-model="form.gender">
              <option value="">Select Gender</option>
              <option value="male">Male</option>
              <option value="female">Female</option>
              <option value="non_binary">Non-Binary</option>
              <option value="other">Other</option>
              <option value="prefer_not_to_say">Prefer not to say</option>
            </select>
          </div>

          <div class="form-group">
            <label for="gender_preference">Interested In</label>
            <select id="gender_preference" v-model="form.gender_preference">
              <option value="all">Everyone</option>
              <option value="male">Men</option>
              <option value="female">Women</option>
              <option value="non_binary">Non-Binary</option>
            </select>
          </div>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label for="relationship_goal">Relationship Goal</label>
            <select id="relationship_goal" v-model="form.relationship_goal">
              <option value="">Select Goal</option>
              <option value="friendship">Friendship</option>
              <option value="casual_dating">Casual Dating</option>
              <option value="serious_relationship">Serious Relationship</option>
              <option value="marriage">Marriage</option>
            </select>
          </div>

          <div class="form-group">
            <label for="occupation">Occupation</label>
            <input
              id="occupation"
              v-model="form.occupation"
              type="text"
              placeholder="Your job"
            />
          </div>
        </div>

        <div class="form-group checkbox-group">
          <label>
            <input v-model="form.visibility" type="checkbox" />
            Make my profile public
          </label>
        </div>

        <div v-if="errors.general" class="error">
          {{ errors.general[0] }}
        </div>

        <div class="form-actions">
          <button
            type="button"
            class="btn-secondary"
            @click="router.push('/profile')"
          >
            Cancel
          </button>
          <button type="submit" :disabled="loading">
            {{
              loading
                ? "Saving..."
                : isEdit
                  ? "Update Profile"
                  : "Create Profile"
            }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from "vue";
import { useRouter } from "vue-router";
import profileService from "../services/profileService";

const router = useRouter();
const loading = ref(false);
const errors = ref({});
const isEdit = ref(false);

const form = reactive({
  name: "",
  age: null,
  bio: "",
  interests: "",
  gender: "",
  gender_preference: "all",
  relationship_goal: "",
  occupation: "",
  visibility: true,
});

const loadProfile = async () => {
  try {
    const data = await profileService.getProfile();
    isEdit.value = true;

    form.name = data.name;
    form.age = data.age;
    form.bio = data.bio || "";
    form.interests = data.interests?.join(", ") || "";
    form.gender = data.gender || "";
    form.gender_preference = data.gender_preference || "all";
    form.relationship_goal = data.relationship_goal || "";
    form.occupation = data.occupation || "";
    form.visibility = data.visibility !== false;
  } catch (error) {
    if (error.response?.status !== 404) {
      console.error(error);
    }
  }
};

const handleSubmit = async () => {
  errors.value = {};
  loading.value = true;

  try {
    const profileData = {
      ...form,
      interests: form.interests,
    };

    if (isEdit.value) {
      await profileService.updateProfile(profileData);
    } else {
      await profileService.createProfile(profileData);
    }

    router.push("/profile");
  } catch (error) {
    if (error.response?.data?.errors) {
      errors.value = error.response.data.errors;
    } else {
      errors.value = {
        general: ["Failed to save profile. Please try again."],
      };
    }
  } finally {
    loading.value = false;
  }
};

onMounted(loadProfile);
</script>

<style scoped>
.edit-container {
  max-width: 700px;
  margin: 0 auto;
  padding: 40px 20px;
}

.edit-card {
  background: white;
  padding: 40px;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

h2 {
  color: #e91e63;
  margin-bottom: 30px;
  text-align: center;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.form-group {
  margin-bottom: 20px;
}

label {
  display: block;
  margin-bottom: 6px;
  font-weight: 500;
  color: #333;
}

input,
select,
textarea {
  width: 100%;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
  box-sizing: border-box;
  font-family: inherit;
}

input:focus,
select:focus,
textarea:focus {
  outline: none;
  border-color: #e91e63;
}

textarea {
  resize: vertical;
}

.error {
  color: #e53935;
  font-size: 12px;
  margin-top: 4px;
  display: block;
}

.checkbox-group label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.checkbox-group input {
  width: auto;
}

.form-actions {
  display: flex;
  gap: 15px;
  margin-top: 30px;
}

button {
  flex: 1;
  padding: 14px;
  border: none;
  border-radius: 6px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.3s;
}

button[type="submit"] {
  background: #e91e63;
  color: white;
}

button[type="submit"]:hover:not(:disabled) {
  background: #c2185b;
}

button[type="submit"]:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-secondary {
  background: #f5f5f5;
  color: #333;
}

.btn-secondary:hover {
  background: #eee;
}
</style>
