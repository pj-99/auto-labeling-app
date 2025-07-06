<template>
  <div class="max-w-3xl mx-auto sm:px-6 lg:px-8">
    <!-- Header Section -->
    <div class="mb-8">
      <h1 class="text-2xl font-semibold text-gray-900 mb-2">Datasets</h1>
      <p class="text-gray-600">Manage your datasets for image labeling</p>
    </div>

    <!-- Create Dataset Section -->
    <div class="mb-8">
      <UModal v-model:open="openModal">
        <UButton label="Create Dataset" color="secondary" variant="subtle" />
        <template #content>
          <UCard>
            <template #header>
              <div class="flex items-center justify-between">
                <h2 class="text-lg font-medium">Create New Dataset</h2>
              </div>
            </template>

            <div class="flex gap-4 items-center">
              <UInput
                v-model="datasetName"
                placeholder="Enter dataset name"
                size="md"
                class="flex-1"
              />
              <UButton
                color="primary"
                size="md"
                :loading="isCreating"
                :disabled="!datasetName"
                @click="createDataset"
              >
                Create
              </UButton>
            </div>

            <!-- Success Message -->
            <UAlert
              v-if="showSuccess"
              color="green"
              variant="soft"
              title="Success!"
              class="mt-4"
            >
              <template #description>
                Dataset created successfully
              </template>
            </UAlert>
          </UCard>
        </template>
      </UModal>
    </div>

    <!-- Datasets List Section -->
    <div class="mt-12">
      <h2 class="text-xl font-medium mb-4">Your Datasets</h2>
      
      <!-- Loading State -->
      <div v-if="datasetsLoading" class="text-center py-4">
        <p class="text-gray-600">Loading datasets...</p>
      </div>

      <!-- Datasets Grid -->
      <div v-else class="grid grid-cols-1 gap-6">
        <UCard v-for="dataset in datasets" :key="dataset.updatedAt" class="hover:shadow-md transition-shadow cursor-pointer">
          <NuxtLink :to="`/dataset/${dataset.id}`" class="block">
            <div class="flex items-start justify-between">
              <div>
                <h3 class="text-lg font-medium">{{ dataset.name }}</h3>
                <p class="text-sm text-gray-500 mt-1">Updated at{{ formatDate(dataset.createdAt) }}</p>
              </div>
              <UDropdownMenu :items="datasetActions(dataset.id)" @click.stop>
                <UButton color="gray" variant="ghost" icon="i-heroicons-ellipsis-horizontal-20-solid" />
              </UDropdownMenu>
            </div>
            <div class="mt-4">
              <p class="text-sm text-gray-600">{{ dataset.images?.length || 0 }} images</p>
            </div>
          </NuxtLink>
        </UCard>

        <!-- Empty State -->
        <div v-if="!datasetsLoading && datasets.length === 0" class="text-center py-4">
          <p class="text-gray-600">No datasets found. Create one above to get started.</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">

import { ref, computed } from 'vue'
import { useQuery, useMutation } from '@vue/apollo-composable'
import { gql } from 'graphql-tag'
import { UDropdownMenu } from '#components'
const openModal = ref(false)

definePageMeta({
  layout: 'default'
})

interface Dataset {
  id: string
  name: string
  createdAt: string
  updatedAt: string
  createdBy: string
  images: any[]
}

interface DatasetsQueryResult {
  datasets: Dataset[]
}

const datasetName = ref('')
const isCreating = ref(false)
const showSuccess = ref(false)

const toast = useToast()

function showSuccessToast() {
  toast.add({
    description: 'Your action was completed successfully.',
    color: 'primary',
    progress: false,
    duration: 5000,
    close: false,
  })
}


// GraphQL Queries
const DATASETS_QUERY = gql`
  query GetDatasets($userId: UUID!) {
    datasets(userId: $userId) {
      id
      name
      createdAt
      updatedAt
      createdBy
      images {
        id
      }
    }
  }
`

const CREATE_DATASET_MUTATION = gql`
  mutation CreateDataset($userId: UUID!, $name: String!) {
    createDataset(userId: $userId, name: $name) {
      id
      name
      createdAt
      updatedAt
      createdBy
      images {
        id
      }
    }
  }
`

// TODO: Replace with actual user ID from auth system
const userId = '123e4567-e89b-12d3-a456-426614174000'

const { result: datasetsData, loading: datasetsLoading, refetch: refresh } = useQuery<DatasetsQueryResult>(DATASETS_QUERY, {
  userId
})

const datasets = computed(() => {
  return datasetsData.value?.datasets || []
})

const { mutate: createDatasetMutation, loading: createLoading } = useMutation(CREATE_DATASET_MUTATION)

const createDataset = async () => {
  console.log('createDataset')
  if (!datasetName.value) return
  console.log('datasetName', datasetName.value)
  isCreating.value = true
  
  try {
    await createDatasetMutation({
      userId,
      name: datasetName.value
    })
    
    // Reset form and show success
    datasetName.value = ''
    showSuccess.value = true
    setTimeout(() => {
      showSuccess.value = false
    }, 3000)
    openModal.value = false
    showSuccessToast()
    // Refetch datasets
    await refresh()
  } catch (error) {
    console.error('Error creating dataset:', error)
  } finally {
    isCreating.value = false
  }
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleString()
}

const datasetActions = (datasetId: string) => [
  [{
    label: 'Edit',
    icon: 'i-heroicons-pencil-square',
    click: () => {
      // TODO: Implement edit functionality
      console.log('Edit dataset:', datasetId)
    }
  },
  {
    label: 'Delete',
    icon: 'i-heroicons-trash',
    click: () => {
      // TODO: Implement delete functionality
      console.log('Delete dataset:', datasetId)
    }
  }]
]
</script> 