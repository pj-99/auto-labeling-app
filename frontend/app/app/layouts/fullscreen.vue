<template>
    <div class="min-h-screen bg-default">
      <AppNavbar />
      <div class="w-full px-2 sm:px-4 py-4">
        <slot />
      </div>
    </div>
  </template>
  
  <script setup lang="ts">
  import AppNavbar from '~/components/AppNavbar.vue'
  </script>