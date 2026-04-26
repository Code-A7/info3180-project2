<template>
  <div class="relative inline-block" :class="sizeClass">
    <img
      v-if="src"
      :src="src"
      :alt="name"
      class="rounded-full object-cover bg-gray-200 dark:bg-gray-700"
      :class="sizeClass"
    />
    <div
      v-else
      class="rounded-full bg-gradient-to-br from-primary-400 to-accent-500 flex items-center justify-center text-white font-medium"
      :class="sizeClass"
    >
      {{ initials }}
    </div>
    <span
      v-if="showOnline && online"
      class="absolute bottom-0 right-0 block rounded-full ring-2 ring-white dark:ring-gray-800"
      :class="onlineIndicatorClass"
    />
  </div>
</template>

<script setup>
import { computed } from "vue";

const props = defineProps({
  src: String,
  name: String,
  size: {
    type: String,
    default: "md",
    validator: (v) => ["xs", "sm", "md", "lg", "xl"].includes(v),
  },
  online: Boolean,
  showOnline: Boolean,
});

const initials = computed(() => {
  if (!props.name) return "?";
  return props.name
    .split(" ")
    .map((n) => n[0])
    .join("")
    .toUpperCase()
    .slice(0, 2);
});

const sizeClass = computed(
  () =>
    ({
      xs: "w-6 h-6 text-xs",
      sm: "w-8 h-8 text-sm",
      md: "w-10 h-10 text-base",
      lg: "w-12 h-12 text-lg",
      xl: "w-16 h-16 text-xl",
    })[props.size],
);

const onlineIndicatorClass = computed(
  () =>
    ({
      xs: "w-2 h-2 bg-green-500",
      sm: "w-2.5 h-2.5 bg-green-500",
      md: "w-3 h-3 bg-green-500",
      lg: "w-3.5 h-3.5 bg-green-500",
      xl: "w-4 h-4 bg-green-500",
    })[props.size],
);
</script>
