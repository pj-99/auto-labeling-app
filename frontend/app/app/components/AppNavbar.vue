<template>
  <nav class="bg-white border-b border-gray-200">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex justify-between h-16">
        <!-- Left side - Logo and main navigation -->
        <div class="flex">
          <!-- Logo -->
          <div class="flex-shrink-0 flex items-center">
            <NuxtLink to="/" class="text-xl font-bold text-gray-900">
              AutoLabel
            </NuxtLink>
          </div>

          <!-- Main Navigation -->
          <div class="hidden sm:ml-6 sm:flex sm:space-x-8">
            <NuxtLink
              to="/dataset"
              class="inline-flex items-center px-1 pt-1 border-b-2"
              :class="[
                $route.path.startsWith('/dataset')
                  ? 'border-primary-500 text-gray-900'
                  : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700'
              ]"
            >
              Datasets
            </NuxtLink>
          </div>
        </div>

        <!-- Right side - User menu -->
        <div class="flex items-center">
          <UButton
            color="gray"
            variant="ghost"
            icon="i-heroicons-user-circle"
          />
        </div>
      </div>
    </div>
  </nav>
</template>

<script setup lang="ts">
// Component is ready for future expansion with more navigation items and user menu
</script> 