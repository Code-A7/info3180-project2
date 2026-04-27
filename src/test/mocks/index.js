import { vi } from "vitest";
import * as services from "./services.js";
import * as composables from "./composables.js";
import { createTestRouter, routerLinkStub } from "./router.js";

// Move all vi.mock() calls to top level as required by vitest 4.x
vi.mock("../services/api", () => ({
  default: services.mockApi,
  get: services.mockApi.get,
  post: services.mockApi.post,
  put: services.mockApi.put,
  delete: services.mockApi.delete,
  patch: services.mockApi.patch,
  apiWithRetry: services.mockApi,
  getToken: vi.fn(),
  getUser: vi.fn(),
  clearAuthData: vi.fn(),
}));

vi.mock("../services/authService", () => ({
  authService: services.mockAuthService,
  validateEmail: services.mockValidateEmail,
  passwordValidation: services.mockAuthService.passwordValidation,
  default: services.mockAuthService,
}));

vi.mock("../services/profileService", () => ({
  profileService: services.mockProfileService,
  default: services.mockProfileService,
}));

vi.mock("../services/matchService", () => ({
  matchService: services.mockMatchService,
  default: services.mockMatchService,
}));

vi.mock("../services/messageService", () => ({
  messageService: services.mockMessageService,
  default: services.mockMessageService,
}));

vi.mock("../services/socketService", () => ({
  socketService: services.mockSocketService,
  default: services.mockSocketService,
}));

vi.mock("../services/notificationService", () => ({
  notificationService: services.mockNotificationService,
  default: services.mockNotificationService,
}));

vi.mock("../services/searchService", () => ({
  searchService: services.mockSearchService,
  default: services.mockSearchService,
}));

vi.mock("../composables/useAuth", () => ({
  useAuth: () => composables.mockUseAuth,
  default: () => composables.mockUseAuth,
}));

vi.mock("../composables/useNotifications", () => ({
  useNotifications: () => composables.createMockUseNotifications(),
  default: () => composables.createMockUseNotifications(),
}));

vi.mock("../composables/useMatches", () => ({
  useMatches: () => composables.createMockUseMatches(),
  default: () => composables.createMockUseMatches(),
}));

vi.mock("../composables/useMessages", () => ({
  useMessages: () => composables.createMockUseMessages(),
  default: () => composables.createMockUseMessages(),
}));

export { services, composables, createTestRouter, routerLinkStub };

export const setupCentralMocks = (vi) => {
  // Mocks are now at top level, this function can be removed or kept for backward compatibility
};

export const resetAllMocks = () => {
  services.mockApi.get.mockClear();
  services.mockApi.post.mockClear();
  services.mockApi.put.mockClear();

  services.mockAuthService.login.mockClear();
  services.mockAuthService.logout.mockClear();
  services.mockAuthService.getStoredUser.mockClear();

  services.mockProfileService.getProfile.mockClear();
  services.mockMatchService.getMatches.mockClear();
  services.mockMessageService.getConversations.mockClear();
  services.mockSocketService.on.mockClear();
};

export const setAuthUser = (user) => {
  services.mockAuthService.getStoredUser.mockReturnValue(user);
  services.mockAuthService.isAuthenticated.mockReturnValue(!!user);
};

export const setUnauthenticated = () => {
  services.mockAuthService.getStoredUser.mockReturnValue(null);
  services.mockAuthService.isAuthenticated.mockReturnValue(false);
};

export const setProfileData = (profileData) => {
  services.mockProfileService.getProfile.mockResolvedValue(profileData);
};

export const setNoProfile = () => {
  services.mockProfileService.getProfile.mockRejectedValue(
    new Error("No profile"),
  );
};

export const setMatches = (matches) => {
  services.mockMatchService.getMatches.mockResolvedValue(matches);
};

export const setConversations = (conversations) => {
  services.mockMessageService.getConversations.mockResolvedValue(conversations);
};

export const setMessages = (userId, messages, otherUser = null) => {
  services.mockMessageService.getMessageHistory.mockResolvedValue({
    messages,
    other_user: otherUser || { id: userId, name: "Test User" },
    has_next: false,
    page: 1,
    total_pages: 1,
  });
};
