/**
 * Vue Router configuration
 *
 * This file defines all application routes, their associated components,
 * and authentication requirements. It also handles route guards for
 * authentication and authorization.
 */

import { createRouter, createWebHistory } from "vue-router";
import HomeView from "../views/HomeView.vue";
import { authService } from "../services/authService";

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: "/",
      name: "home",
      component: HomeView,
    },
    {
      path: "/about",
      name: "about",
      component: () => import("../views/AboutView.vue"),
    },
    {
      path: "/register",
      name: "register",
      component: () => import("../views/RegisterView.vue"),
      meta: { guest: true },
    },
    {
      path: "/login",
      name: "login",
      component: () => import("../views/LoginView.vue"),
      meta: { guest: true },
    },
    {
      path: "/profile",
      component: () => import("../views/ProfileView.vue"),
      meta: { requiresAuth: true },
      children: [
        {
          path: "",
          name: "profile",
          component: () => import("../views/ProfileView.vue"),
          meta: { requiresAuth: true },
        },
        {
          path: ":userId",
          name: "viewProfile",
          component: () => import("../views/ProfileView.vue"),
          meta: { requiresAuth: true },
        },
      ],
    },
    {
      path: "/profile/edit",
      name: "editProfile",
      component: () => import("../views/EditProfileView.vue"),
      meta: { requiresAuth: true },
    },
    {
      path: "/profile/settings",
      name: "profileSettings",
      component: () => import("../views/SettingsView.vue"),
      meta: { requiresAuth: true },
    },
    {
      path: "/settings",
      name: "settings",
      component: () => import("../views/SettingsView.vue"),
      meta: { requiresAuth: true },
    },
    {
      path: "/verify/:token",
      name: "verify",
      component: () => import("../views/VerifyView.vue"),
    },
    {
      path: "/browse",
      name: "browse",
      component: () => import("../views/BrowseView.vue"),
      meta: { requiresAuth: true },
    },
    {
      path: "/matches",
      name: "matches",
      component: () => import("../views/MatchesView.vue"),
      meta: { requiresAuth: true },
    },
    {
      path: "/notifications",
      name: "notifications",
      component: () => import("../views/NotificationsView.vue"),
      meta: { requiresAuth: true },
    },
    {
      path: "/messages",
      name: "messages",
      component: () => import("../views/MessagesView.vue"),
      meta: { requiresAuth: true },
      children: [
        {
          path: "",
          name: "conversations",
          component: () => import("../views/ConversationsView.vue"),
          meta: { requiresAuth: true },
        },
        {
          path: ":userId",
          name: "chat",
          component: () => import("../views/ChatView.vue"),
          meta: { requiresAuth: true },
        },
      ],
    },
    {
      path: "/conversations",
      name: "conversationsLegacy",
      redirect: "/messages",
    },
    {
      path: "/chat/:userId",
      name: "chatLegacy",
      redirect: (to) => ({
        name: "chat",
        params: { userId: to.params.userId },
      }),
    },
    {
      path: "/search",
      name: "search",
      component: () => import("../views/SearchView.vue"),
      meta: { requiresAuth: true },
    },
    {
      path: "/favorites",
      name: "favorites",
      component: () => import("../views/FavoritesView.vue"),
      meta: { requiresAuth: true },
    },
    {
      path: "/:pathMatch(.*)*",
      name: "notFound",
      component: () => import("../views/NotFoundView.vue"),
    },
  ],
});

router.beforeEach((to, from, next) => {
  const isAuthenticated = authService.isAuthenticated();

  if (to.meta.requiresAuth && !isAuthenticated) {
    next({ name: "login", query: { redirect: to.fullPath } });
  } else if (to.meta.guest && isAuthenticated) {
    next({ name: "home" });
  } else {
    next();
  }
});

export default router;
