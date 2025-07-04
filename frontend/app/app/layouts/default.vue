<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Navigation -->
    <AppNavbar />
    
    <!-- Main Content -->
    <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-10">
      <slot />
    </div>
  </div>
</template>

<script setup lang="ts">
// Import the navbar component
import AppNavbar from '~/components/AppNavbar.vue'
</script> 