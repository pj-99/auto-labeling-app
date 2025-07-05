<template>
  <div class="max-w-3xl mx-auto sm:px-6 lg:px-8">
    <!-- Header Section -->
    <div class="mb-8">
      <div class="flex items-center gap-3 mb-2">
        <UButton
          icon="i-heroicons-arrow-left"
          variant="ghost"
          color="primary"
          to="/dataset"
        />
        <h1 class="text-2xl font-semibold text-gray-900">{{ dataset?.name }}</h1>
      </div>
      <p class="text-gray-600">Upload and manage images in this dataset</p>
      <div class="mt-2 flex items-center gap-2">
        <UBadge variant="soft" size="md">{{ dataset?.images?.length || 0 }} images</UBadge>
        <UBadge variant="outline" size="md">Created {{ formatDate(dataset?.createdAt) }}</UBadge>
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
    <div class="mt-12 mb-12">
      <h2 class="text-xl font-medium mb-4">Dataset Images</h2>
      
      <div v-if="loading" class="text-center py-8">
        <p class="text-gray-600">Loading images...</p>
      </div>
      
      <div v-else class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
        <NuxtLink 
          v-for="image in dataset?.images" 
          :key="image.id" 
          :to="`/image/${image.id}`"
          class="aspect-square relative overflow-hidden rounded-lg bg-gray-100 group hover:ring-2 hover:ring-primary-500 transition-all duration-200"
        >
          <NuxtImg 
            :src="image.imageUrl" 
            :alt="image.imageName"
            class="absolute inset-0 w-full h-full object-cover group-hover:scale-105 transition-transform duration-200"
            loading="lazy"
            sizes="(min-width: 768px) 25vw, (min-width: 640px) 33vw, 50vw"
            :imgAttrs="{
              class: 'absolute inset-0 w-full h-full object-cover'
            }"
          />
          <div class="absolute inset-x-0 bottom-0 bg-gradient-to-t from-black/50 to-transparent p-4 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
            <p class="text-white text-sm truncate">{{ image.imageName }}</p>
          </div>
        </NuxtLink>
      </div>

      <!-- Empty State -->
      <div v-if="!loading && (!dataset?.images || dataset.images.length === 0)" class="text-center py-8">
        <p class="text-gray-600">No images found. Upload some images to get started.</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">

import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'
import { useToast } from '#imports'
import { useQuery, useMutation } from '@vue/apollo-composable'
import { gql } from 'graphql-tag'

interface Image {
  id: string
  imageName: string
  imageUrl: string
  createdAt: string
  updatedAt: string
  caption: string
  createdBy: string
}

interface Dataset {
  id: string
  name: string
  createdAt: string
  updatedAt: string
  createdBy: string
  images: Image[]
}

const route = useRoute()
const datasetId = route.params.id
const fileInput = ref<HTMLInputElement | null>(null)
const uploading = ref(false)
const toast = useToast()

// TODO: Replace with actual user ID from auth system
const userId = '123e4567-e89b-12d3-a456-426614174000'

// GraphQL Queries
const DATASET_QUERY = gql`
  query GetDatasets($userId: UUID!) {
    datasets(userId: $userId) {
      id
      name
      createdAt
      updatedAt
      createdBy
      images {
        id
        imageName
        imageUrl
        createdAt
        updatedAt
        caption
        createdBy
      }
    }
  }
`

const INSERT_IMAGE_MUTATION = gql`
  mutation InsertImageToDataset($userId: UUID!, $datasetId: UUID!, $gcsFileName: String!, $imageName: String!, $imageType: String!) {
    insertImageToDataset(userId: $userId, datasetId: $datasetId, gcsFileName: $gcsFileName, imageName: $imageName, imageType: $imageType) {
      id
      imageName
      imageUrl  
      createdAt
      updatedAt
      caption
      createdBy
    }
  }
`

// Query for dataset data
const { result: datasetsData, loading, refetch } = useQuery(DATASET_QUERY, {
  userId
})

// Get the current dataset from the query result
const dataset = computed(() => {
  return datasetsData.value?.datasets.find((d: Dataset) => d.id === datasetId)
})

// Mutation for image upload
const { mutate: insertImageMutation } = useMutation(INSERT_IMAGE_MUTATION)

const handleUploadClick = () => {
  fileInput.value?.click()
}

const formatDate = (dateString: string) => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}

// Function to get signed URL from FastAPI
const getSignedUrl = async (contentType: string) => {
  const { public: { apiBase } } = useRuntimeConfig()
  console.log('API base:', apiBase)

  try {
    const response = await fetch(`${apiBase}/generate-signed-url`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ content_type: contentType }),
    })
    
    if (!response.ok) {
      throw new Error('Failed to get signed URL')
    }
    
    return await response.json()
  } catch (error) {
    console.error('Error getting signed URL:', error)
    throw error
  }
}

// Function to upload file using signed URL
const uploadFileToGCS = async (file: File, signedUrl: string) => {
  try {
    const response = await fetch(signedUrl, {
      method: 'PUT',
      headers: {
        'Content-Type': file.type,
      },
      body: file,
    })
    
    if (!response.ok) {
      throw new Error('Failed to upload file to storage')
    }
  } catch (error) {
    console.error('Error uploading to GCS:', error)
    throw error
  }
}

const handleFileChange = async (event: Event) => {
  const input = event.target as HTMLInputElement
  if (!input.files?.length) return

  uploading.value = true
  try {
    // Process each file
    for (const file of Array.from(input.files)) {

      // Step 1: Get signed URL for the file
      const { url: signedUrl, filename } = await getSignedUrl(file.type)
      
      // Step 2: Upload the file to GCS using the signed URL
      await uploadFileToGCS(file, signedUrl)
      
      // Step 3: Insert image record via GraphQL mutation
      await insertImageMutation({
        userId,
        datasetId,
        gcsFileName: filename,
        imageName: file.name,
        imageType: file.type
      })
    }

    // Refetch dataset to update the UI
    await refetch()

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
    console.error('Upload error:', error)
    // Show error notification
    toast.add({
      title: 'Failed to upload images',
      description: error instanceof Error ? error.message : 'Unknown error occurred',
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