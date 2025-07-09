<template>
  <UApp :toaster="{ position: 'bottom-center' }">
    <NuxtLayout>
      <NuxtPage />
    </NuxtLayout>
  </UApp>
</template>

<script setup lang="ts">
import { loadErrorMessages, loadDevMessages } from '@apollo/client/dev'

// TODO
loadDevMessages()
loadErrorMessages()
</script>
