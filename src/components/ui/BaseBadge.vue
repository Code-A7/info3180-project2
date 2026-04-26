<template>
  <span :class="[badgeClasses, variantClasses]">
    <slot />
  </span>
</template>

<script setup>
import { computed } from "vue";

const props = defineProps({
  variant: {
    type: String,
    default: "primary",
    validator: (v) =>
      ["primary", "success", "warning", "danger", "gray"].includes(v),
  },
  dot: Boolean,
});

const variantClasses = computed(
  () =>
    ({
      primary:
        "bg-primary-100 text-primary-800 dark:bg-primary-900/30 dark:text-primary-300",
      success:
        "bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300",
      warning:
        "bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-300",
      danger: "bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300",
      gray: "bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300",
    })[props.variant],
);

const badgeClasses =
  "inline-flex items-center justify-center px-2.5 py-0.5 text-xs font-medium rounded-full";
</script>
