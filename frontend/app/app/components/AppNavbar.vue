
<script setup lang="ts">
import { useRoute, useRouter } from 'vue-router'

const colorMode = useColorMode()

const isDark = computed({
  get() {
    return colorMode.value === 'dark'
  },
  set(_isDark) {
    colorMode.preference = _isDark ? 'dark' : 'light'
  },
})

const route = useRoute()
const router = useRouter()

// Show back button on specific routes
const showBackButton = computed(() => {
  return (
    route.path.startsWith('/image/') ||
    (route.path.startsWith('/dataset/') && route.params.id)
  )
})
</script>

<template>
  <nav>
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex justify-between h-16">
        <!-- Left side - Logo and main navigation -->
        <div class="flex">
          <!-- Back Button (when needed) -->
          <div
            v-if="showBackButton"
            class="flex-shrink-0 flex items-center mr-4"
          >
            <UButton
              icon="i-heroicons-arrow-left"
              variant="ghost"
              color="neutral"
              @click="router.back()"
            />
          </div>

          <!-- Logo -->
          <div class="flex-shrink-0 flex items-center">
            <NuxtLink to="/" class="text-xl font-bold"> AutoLabel </NuxtLink>
          </div>

          <!-- Main Navigation -->
          <div class="hidden sm:ml-6 sm:flex sm:space-x-8">
            <NuxtLink
              to="/dataset"
              class="inline-flex items-center px-1 pt-1 border-b-2"
              :class="[
                $route.path.startsWith('/dataset')
                  ? 'border-primary-500 '
                  : 'border-transparent',
              ]"
            >
              Datasets
            </NuxtLink>
          </div>
        </div>

        <!-- Right side - User menu -->
        <div class="flex items-center">
          <UButton variant="ghost" icon="i-heroicons-user-circle" />
          <!-- Color mode toggle -->
          <UButton
            :icon="isDark ? 'i-lucide-moon' : 'i-lucide-sun'"
            color="neutral"
            variant="ghost"
            @click="isDark = !isDark"
          />
        </div>
      </div>
    </div>
  </nav>
</template>
