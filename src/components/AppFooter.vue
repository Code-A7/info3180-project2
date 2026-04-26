<template>
  <footer
    class="bg-gray-50 dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700 mt-auto"
  >
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div class="flex flex-col md:flex-row justify-between items-center gap-4">
        <div class="flex items-center space-x-2">
          <div
            class="w-8 h-8 rounded-full bg-gradient-to-br from-primary-500 to-accent-500 flex items-center justify-center"
          >
            <span class="text-white font-bold text-sm">D</span>
          </div>
          <span class="text-lg font-bold text-gray-700 dark:text-gray-300">
            DriftDater
          </span>
        </div>

        <div
          class="flex items-center space-x-6 text-sm text-gray-500 dark:text-gray-400"
        >
          <router-link
            to="/about"
            class="hover:text-primary-600 dark:hover:text-primary-400 transition-colors"
          >
            About
          </router-link>
          <router-link
            to="/login"
            class="hover:text-primary-600 dark:hover:text-primary-400 transition-colors"
          >
            Login
          </router-link>
          <router-link
            to="/register"
            class="hover:text-primary-600 dark:hover:text-primary-400 transition-colors"
          >
            Register
          </router-link>
        </div>

        <div class="text-sm text-gray-500 dark:text-gray-400">
          &copy; {{ year }} DriftDater. All rights reserved.
        </div>
      </div>
    </div>
  </footer>
</template>

<script setup>
const year = new Date().getFullYear();
</script>
