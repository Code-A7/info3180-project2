import js from "@eslint/js";
import pluginVue from "eslint-plugin-vue";
import skipPrettier from "eslint-config-prettier";
import globals from "globals";

export default [
  {
    ignores: [
      "dist/**",
      ".venv/**",
      "node_modules/**",
      "coverage/**",
      "htmlcov/**",
      "playwright-report/**",
    ],
  },
  js.configs.recommended,
  ...pluginVue.configs["flat/recommended"],
  {
    languageOptions: {
      globals: {
        ...globals.browser,
        ...globals.node,
        ...globals.serviceworker,
      },
    },
  },
  {
    files: ["e2e/**/*.js"],
    languageOptions: {
      globals: {
        ...globals.node,
      },
    },
  },
  {
    files: ["src/__tests__/**/*.js", "src/test/**/*.js"],
    languageOptions: {
      globals: {
        ...globals.browser,
        ...globals.node,
        vi: "readonly",
        describe: "readonly",
        it: "readonly",
        expect: "readonly",
        beforeEach: "readonly",
        afterEach: "readonly",
        beforeAll: "readonly",
        afterAll: "readonly",
      },
    },
  },
  {
    files: ["**/*.js", "**/*.vue"],
    rules: {
      "vue/multi-word-component-names": "off",
      "no-unused-vars": ["warn", { argsIgnorePattern: "^_" }],
      "vue/require-default-prop": "off",
      "no-undef": "error",
    },
  },
  skipPrettier,
];
