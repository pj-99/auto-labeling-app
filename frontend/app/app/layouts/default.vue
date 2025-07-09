<template>
  <div class="min-h-screen">
    <!-- Navigation -->
    <AppNavbar />

    <!-- Main Content -->
    <div class="mx-auto px-4 sm:px-6 lg:px-8 py-10">
      <slot />
    </div>
  </div>
</template>

<script setup lang="ts">
// Import the navbar component
import AppNavbar from '~/components/AppNavbar.vue'
</script>
