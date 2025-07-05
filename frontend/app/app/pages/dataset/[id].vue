<template>
  <div class="max-w-3xl mx-auto sm:px-6 lg:px-8">
    <!-- Header Section -->
    <div class="mb-8">
      <div class="flex items-center gap-3 mb-2">
        <UButton
          icon="i-heroicons-arrow-left"
          variant="ghost"
          color="gray"
          to="/dataset"
        />
        <h1 class="text-2xl font-semibold text-gray-900">{{ dataset.name }}</h1>
      </div>
      <p class="text-gray-600">Upload and manage images in this dataset</p>
      <div class="mt-2 flex items-center gap-2">
        <UBadge color="primary" size="sm">{{ images.length }} images</UBadge>
        <UBadge color="gray" size="sm">Created {{ formatDate(dataset.createdAt) }}</UBadge>
      </div>
    </div>

    <!-- Upload Section -->
    <div class="mb-12">
      <h2 class="text-xl font-medium mb-4">Upload Images</h2>
      <div class="bg-gray-50 border-2 border-dashed border-gray-300 rounded-lg p-8">
        <div class="text-center">
          <UIcon name="i-heroicons-cloud-arrow-up" class="mx-auto h-12 w-12 text-gray-400" />
          <div class="mt-4">
            <h3 class="text-lg font-semibold">Drop Files Here</h3>
            <p class="mt-1 text-sm text-gray-500">Drag and drop your images here, or click to select files</p>
          </div>
          <UButton 
            class="mt-4" 
            @click="handleUploadClick"
            :loading="uploading"
          >
            Select Files
          </UButton>
          <input 
            ref="fileInput" 
            type="file" 
            multiple 
            accept="image/*" 
            class="hidden" 
            @change="handleFileChange"
          />
        </div>
      </div>
    </div>

    <!-- Images Grid Section -->
    <div class="mt-12">
      <h2 class="text-xl font-medium mb-4">Dataset Images</h2>
      
      <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
        <div 
          v-for="image in images" 
          :key="image.id" 
          class="aspect-square relative overflow-hidden rounded-lg bg-gray-100"
        >
          <NuxtImg 
            :src="image.url" 
            :alt="image.name"
            class="absolute inset-0 w-full h-full object-cover"
            loading="lazy"
            sizes="(min-width: 768px) 25vw, (min-width: 640px) 33vw, 50vw"
            :imgAttrs="{
              class: 'absolute inset-0 w-full h-full object-cover'
            }"
          />
        </div>
      </div>

      <!-- Empty State -->
      <div v-if="images.length === 0" class="text-center py-8">
        <p class="text-gray-600">No images found. Upload some images to get started.</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRoute } from 'vue-router'
import { useToast } from '#imports'

const route = useRoute()
const datasetId = route.params.id
const fileInput = ref<HTMLInputElement | null>(null)
const uploading = ref(false)
const toast = useToast()

// Mock dataset data
const dataset = ref({
  id: datasetId,
  name: 'Street Signs Dataset',
  createdAt: '2024-03-15T10:30:00Z',
  updatedAt: '2024-03-15T10:30:00Z'
})

// Mock data for images with more realistic names and variety
const images = ref([
  {
    id: '1',
    name: 'stop_sign_01.jpg',
    url: 'https://i.imgur.com/TK0hhSP.jpg'
  },
  {
    id: '2',
    name: 'yield_sign_02.jpg',
    url: 'https://i.imgur.com/TK0hhSP.jpg'
  },
  {
    id: '3',
    name: 'speed_limit_30.jpg',
    url: 'https://i.imgur.com/TK0hhSP.jpg'
  },
  {
    id: '4',
    name: 'crosswalk_sign_01.jpg',
    url: 'https://i.imgur.com/TK0hhSP.jpg'
  },
  {
    id: '5',
    name: 'no_parking_sign.jpg',
    url: 'https://i.imgur.com/TK0hhSP.jpg'
  },
  {
    id: '6',
    name: 'one_way_sign_02.jpg',
    url: 'https://i.imgur.com/TK0hhSP.jpg'
  },
  {
    id: '7',
    name: 'stop_sign_night_01.jpg',
    url: 'https://i.imgur.com/TK0hhSP.jpg'
  },
  {
    id: '8',
    name: 'yield_sign_rain.jpg',
    url: 'https://i.imgur.com/TK0hhSP.jpg'
  },
  {
    id: '9',
    name: 'speed_limit_55.jpg',
    url: 'https://i.imgur.com/TK0hhSP.jpg'
  }
])

const handleUploadClick = () => {
  fileInput.value?.click()
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}

const handleFileChange = async (event: Event) => {
  const input = event.target as HTMLInputElement
  if (!input.files?.length) return

  uploading.value = true
  
  try {
    // Mock upload process
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    // Add new images to the grid
    Array.from(input.files).forEach((file, index) => {
      console.log('Processing file:', {
        name: file.name,
        size: file.size,
        type: file.type
      })
      images.value.push({
        id: `new-${Date.now()}-${index}`,
        name: file.name,
        url: 'https://i.imgur.com/TK0hhSP.jpg' // Using mock image URL
      })
    })

    // Show success notification
    toast.add({
      title: `Successfully uploaded ${input.files.length} images`,
      color: 'success',
      duration: 5000,
      progress: false,
      close: false,
      icon: 'i-heroicons-check-circle'
    })
  } catch (error) {
    // Show error notification
    toast.add({
      title: 'Failed to upload images',
      color: 'error',
      duration: 5000,
      icon: 'i-heroicons-exclamation-triangle'
    })
  } finally {
    uploading.value = false
    // Reset input
    if (fileInput.value) {
      fileInput.value.value = ''
    }
  }
}
</script> 