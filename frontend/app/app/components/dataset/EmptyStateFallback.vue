<script setup lang="ts">
interface Props {
  title?: string
  description?: string
  icon?: string
  gridItems?: number
  showGrid?: boolean
}
withDefaults(defineProps<Props>(), {
  title: 'No content available',
  description: 'Content will appear here once added',
  icon: 'i-heroicons-cube-transparent',
  gridItems: 32,
  showGrid: true
})
</script>

<template>
  <div class="relative py-50">
    <!-- Animated grid background -->
    <div v-if="showGrid" class="absolute inset-0 overflow-hidden opacity-50">
      <div class="absolute inset-0 bg-gradient-to-br from-primary-500/10 via-transparent to-purple-500/10" />
      <div class="grid grid-cols-8 gap-4 rotate-12 scale-150">
        <div
          v-for="i in gridItems"
          :key="i"
          class="aspect-square rounded-lg bg-gradient-to-br from-gray-200 to-gray-300 dark:from-gray-700 dark:to-gray-800 animate-pulse"
          :style="{ animationDelay: `${i * 0.1}s` }"
        />
      </div>
    </div>

    <!-- Content -->
    <div class="relative text-center">
      <div class="inline-block p-3 bg-gray-100 dark:bg-gray-800 rounded-full mb-4">
        <UIcon 
          :name="icon" 
          class="w-8 h-8 text-gray-400 animate-spin-slow" 
        />
      </div>
      <h3 class="text-lg font-medium text-gray-600 dark:text-gray-300">
        {{ title }}
      </h3>
      <p class="text-sm text-gray-500 dark:text-gray-400 mt-1">
        {{ description }}
      </p>
      
      <!-- Optional slot for additional content (like action buttons) -->
      <div v-if="$slots.action" class="mt-4">
        <slot name="action" />
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Custom animation for slow spin */
@keyframes spin-slow {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.animate-spin-slow {
  animation: spin-slow 3s linear infinite;
}
</style>