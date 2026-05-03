<template>
  <div class="about-container">
    <section class="hero">
      <div class="hero-content">
        <div class="logo">
          <div class="logo-icon">
            <span>D</span>
          </div>
          <h1>DriftDater</h1>
        </div>
        <p class="tagline">
          Find meaningful connections in a world full of possibilities
        </p>
        <div class="cta-buttons">
          <router-link to="/register" class="btn-primary"
            >Get Started</router-link
          >
          <router-link to="/login" class="btn-secondary">Sign In</router-link>
        </div>
      </div>
    </section>

    <section class="features">
      <h2>Everything You Need to Find Love</h2>
      <p class="section-desc">
        Discover features designed to help you make genuine connections
      </p>

      <div class="features-grid">
        <div class="feature-card">
          <div class="feature-icon">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="32"
              height="32"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
            >
              <circle cx="12" cy="12" r="10" />
              <polygon
                points="16.24 7.76 14.12 14.12 7.76 16.24 9.88 9.88 16.24 7.76"
              />
            </svg>
          </div>
          <h3>Discover</h3>
          <p>
            Browse through profiles tailored to your preferences and find people
            who share your interests.
          </p>
        </div>

        <div class="feature-card">
          <div class="feature-icon">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="32"
              height="32"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
            >
              <path
                d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z"
              />
            </svg>
          </div>
          <h3>Match</h3>
          <p>
            When both people feel the connection, it's a match! Start building
            something special together.
          </p>
        </div>

        <div class="feature-card">
          <div class="feature-icon">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="32"
              height="32"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
            >
              <path
                d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"
              />
            </svg>
          </div>
          <h3>Connect</h3>
          <p>
            Chat in real-time with your matches. Share your thoughts, make
            plans, and get to know each other.
          </p>
        </div>

        <div class="feature-card">
          <div class="feature-icon">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="32"
              height="32"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
            >
              <circle cx="11" cy="11" r="8" />
              <path d="m21 21-4.3-4.3" />
            </svg>
          </div>
          <h3>Search</h3>
          <p>
            Advanced filters help you find exactly what you're looking for. Age,
            location, interests, and more.
          </p>
        </div>

        <div class="feature-card">
          <div class="feature-icon">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="32"
              height="32"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
            >
              <path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z" />
            </svg>
          </div>
          <h3>Favorites</h3>
          <p>
            Save profiles you're interested in and revisit them anytime. Never
            lose a potential connection.
          </p>
        </div>

        <div class="feature-card">
          <div class="feature-icon">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="32"
              height="32"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
            >
              <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10" />
              <path d="m9 12 2 2 4-4" />
            </svg>
          </div>
          <h3>Safe & Secure</h3>
          <p>
            Your privacy matters. Control your visibility and block anyone who
            makes you uncomfortable.
          </p>
        </div>
      </div>
    </section>

    <section class="how-it-works">
      <h2>How It Works</h2>
      <p class="section-desc">Three simple steps to find your perfect match</p>

      <div class="steps">
        <div class="step">
          <div class="step-number">1</div>
          <h3>Create Your Profile</h3>
          <p>
            Sign up and tell us about yourself. Add photos, share your
            interests, and let your personality shine.
          </p>
        </div>

        <div class="step-connector"></div>

        <div class="step">
          <div class="step-number">2</div>
          <h3>Discover & Match</h3>
          <p>
            Browse profiles that match your preferences. Like what you see? Make
            a connection. It's that simple.
          </p>
        </div>

        <div class="step-connector"></div>

        <div class="step">
          <div class="step-number">3</div>
          <h3>Start Chatting</h3>
          <p>
            When you match, the conversation begins. Get to know each other and
            see where it leads.
          </p>
        </div>
      </div>
    </section>

    <section class="safety">
      <div class="safety-content">
        <h2>Your Safety Matters</h2>
        <p>
          We're committed to creating a safe and respectful community for
          everyone.
        </p>

        <div class="safety-features">
          <div class="safety-item">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="24"
              height="24"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
            >
              <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10" />
              <path d="m9 12 2 2 4-4" />
            </svg>
            <span>Profile verification</span>
          </div>
          <div class="safety-item">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="24"
              height="24"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
            >
              <rect width="18" height="11" x="3" y="11" rx="2" ry="2" />
              <path d="M7 11V7a5 5 0 0 1 10 0v4" />
            </svg>
            <span>Privacy controls</span>
          </div>
          <div class="safety-item">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="24"
              height="24"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
            >
              <circle cx="12" cy="12" r="10" />
              <line x1="4.93" x2="19.07" y1="4.93" y2="19.07" />
            </svg>
            <span>Block & report users</span>
          </div>
          <div class="safety-item">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="24"
              height="24"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
            >
              <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
              <circle cx="9" cy="7" r="4" />
              <line x1="17" x2="22" y1="11" y2="11" />
            </svg>
            <span>Community guidelines</span>
          </div>
        </div>
      </div>
    </section>

    <section class="stats">
      <div class="stat-item">
        <div class="stat-number">10K+</div>
        <div class="stat-label">Active Users</div>
      </div>
      <div class="stat-item">
        <div class="stat-number">5K+</div>
        <div class="stat-label">Successful Matches</div>
      </div>
      <div class="stat-item">
        <div class="stat-number">98%</div>
        <div class="stat-label">User Satisfaction</div>
      </div>
    </section>

    <section class="cta">
      <h2>Ready to Find Your Match?</h2>
      <p>
        Join thousands of people who are already making meaningful connections
        on DriftDater.
      </p>
      <router-link to="/register" class="btn-primary-large"
        >Create Free Account</router-link
      >
    </section>
  </div>
</template>

<script setup>
const currentYear = new Date().getFullYear();
</script>

<style scoped>
.about-container {
  overflow-x: hidden;
}

.hero {
  min-height: calc(100vh - 200px);
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(
    135deg,
    rgba(20, 184, 166, 0.1) 0%,
    rgba(139, 92, 246, 0.1) 100%
  );
  padding: 4rem 1.5rem;
  text-align: center;
}

:global(.dark) .hero {
  background: linear-gradient(
    135deg,
    rgba(20, 184, 166, 0.05) 0%,
    rgba(139, 92, 246, 0.05) 100%
  );
}

.hero-content {
  max-width: 600px;
}

.logo {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.logo-icon {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  background: linear-gradient(135deg, #14b8a6, #8b5cf6);
  display: flex;
  align-items: center;
  justify-content: center;
}

.logo-icon span {
  color: white;
  font-size: 2rem;
  font-weight: bold;
}

.logo h1 {
  font-size: 2.5rem;
  font-weight: 800;
  background: linear-gradient(135deg, #14b8a6, #8b5cf6);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin: 0;
}

.tagline {
  font-size: 1.25rem;
  color: #6b7280;
  margin-bottom: 2rem;
  line-height: 1.6;
}

:global(.dark) .tagline {
  color: #9ca3af;
}

.cta-buttons {
  display: flex;
  gap: 1rem;
  justify-content: center;
  flex-wrap: wrap;
}

.btn-primary {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.875rem 1.5rem;
  background: linear-gradient(135deg, #14b8a6, #0d9488);
  color: white;
  text-decoration: none;
  border-radius: 0.75rem;
  font-weight: 600;
  transition: all 0.2s;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(20, 184, 166, 0.4);
}

.btn-secondary {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.875rem 1.5rem;
  background: #f3f4f6;
  color: #374151;
  text-decoration: none;
  border-radius: 0.75rem;
  font-weight: 600;
  transition: all 0.2s;
}

:global(.dark) .btn-secondary {
  background: #374151;
  color: #f9fafb;
}

.btn-secondary:hover {
  background: #e5e7eb;
}

:global(.dark) .btn-secondary:hover {
  background: #4b5563;
}

.features,
.how-it-works {
  padding: 5rem 1.5rem;
  max-width: 1200px;
  margin: 0 auto;
}

.features h2,
.how-it-works h2 {
  font-size: 2rem;
  font-weight: 700;
  text-align: center;
  color: #111827;
  margin-bottom: 0.5rem;
}

:global(.dark) .features h2,
:global(.dark) .how-it-works h2 {
  color: #f9fafb;
}

.section-desc {
  text-align: center;
  color: #6b7280;
  margin-bottom: 3rem;
}

:global(.dark) .section-desc {
  color: #9ca3af;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.5rem;
}

.feature-card {
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(20, 184, 166, 0.1);
  border-radius: 1rem;
  padding: 1.5rem;
  transition: all 0.3s;
}

:global(.dark) .feature-card {
  background: rgba(31, 41, 55, 0.6);
  border-color: rgba(139, 92, 246, 0.15);
}

.feature-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 40px rgba(20, 184, 166, 0.15);
}

:global(.dark) .feature-card:hover {
  box-shadow: 0 12px 40px rgba(139, 92, 246, 0.15);
}

.feature-icon {
  width: 56px;
  height: 56px;
  border-radius: 0.75rem;
  background: linear-gradient(
    135deg,
    rgba(20, 184, 166, 0.1),
    rgba(139, 92, 246, 0.1)
  );
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 1rem;
  color: #14b8a6;
}

:global(.dark) .feature-icon {
  color: #8b5cf6;
}

.feature-card h3 {
  font-size: 1.125rem;
  font-weight: 700;
  color: #111827;
  margin-bottom: 0.5rem;
}

:global(.dark) .feature-card h3 {
  color: #f9fafb;
}

.feature-card p {
  color: #6b7280;
  font-size: 0.875rem;
  line-height: 1.6;
  margin: 0;
}

:global(.dark) .feature-card p {
  color: #9ca3af;
}

.steps {
  display: flex;
  align-items: flex-start;
  justify-content: center;
  gap: 1rem;
  flex-wrap: wrap;
}

.step {
  flex: 1;
  min-width: 200px;
  max-width: 280px;
  text-align: center;
  padding: 1.5rem;
}

.step-number {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: linear-gradient(135deg, #14b8a6, #0d9488);
  color: white;
  font-size: 1.25rem;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 1rem;
}

:global(.dark) .step-number {
  background: linear-gradient(135deg, #8b5cf6, #7c3aed);
}

.step h3 {
  font-size: 1.125rem;
  font-weight: 700;
  color: #111827;
  margin-bottom: 0.5rem;
}

:global(.dark) .step h3 {
  color: #f9fafb;
}

.step p {
  color: #6b7280;
  font-size: 0.875rem;
  line-height: 1.6;
  margin: 0;
}

:global(.dark) .step p {
  color: #9ca3af;
}

.step-connector {
  width: 60px;
  height: 2px;
  background: linear-gradient(90deg, #14b8a6, #8b5cf6);
  margin-top: 24px;
  flex-shrink: 0;
}

@media (max-width: 768px) {
  .step-connector {
    display: none;
  }
}

.safety {
  background: linear-gradient(
    135deg,
    rgba(20, 184, 166, 0.05) 0%,
    rgba(139, 92, 246, 0.05) 100%
  );
  padding: 5rem 1.5rem;
}

.safety-content {
  max-width: 800px;
  margin: 0 auto;
  text-align: center;
}

.safety h2 {
  font-size: 2rem;
  font-weight: 700;
  color: #111827;
  margin-bottom: 0.5rem;
}

:global(.dark) .safety h2 {
  color: #f9fafb;
}

.safety > .safety-content > p {
  color: #6b7280;
  margin-bottom: 2rem;
}

:global(.dark) .safety > .safety-content > p {
  color: #9ca3af;
}

.safety-features {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 1.5rem;
}

.safety-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  background: rgba(255, 255, 255, 0.8);
  border-radius: 0.5rem;
  color: #374151;
}

:global(.dark) .safety-item {
  background: rgba(31, 41, 55, 0.8);
  color: #f9fafb;
}

.safety-item svg {
  color: #14b8a6;
}

:global(.dark) .safety-item svg {
  color: #8b5cf6;
}

.safety-item span {
  font-weight: 500;
  font-size: 0.875rem;
}

.stats {
  display: flex;
  justify-content: center;
  gap: 4rem;
  padding: 4rem 1.5rem;
  flex-wrap: wrap;
}

.stat-item {
  text-align: center;
}

.stat-number {
  font-size: 3rem;
  font-weight: 800;
  background: linear-gradient(135deg, #14b8a6, #8b5cf6);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  line-height: 1;
  margin-bottom: 0.5rem;
}

.stat-label {
  color: #6b7280;
  font-size: 0.875rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

:global(.dark) .stat-label {
  color: #9ca3af;
}

.cta {
  background: linear-gradient(135deg, #14b8a6, #8b5cf6);
  padding: 5rem 1.5rem;
  text-align: center;
  color: white;
}

.cta h2 {
  font-size: 2rem;
  font-weight: 700;
  margin-bottom: 0.75rem;
  color: white;
}

.cta p {
  max-width: 500px;
  margin: 0 auto 2rem;
  opacity: 0.9;
  line-height: 1.6;
}

.btn-primary-large {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 1rem 2rem;
  background: white;
  color: #14b8a6;
  text-decoration: none;
  border-radius: 0.75rem;
  font-weight: 700;
  font-size: 1.125rem;
  transition: all 0.2s;
}

.btn-primary-large:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.2);
}
</style>
