<template>
  <div class="max-w-3xl mx-auto sm:px-6 lg:px-8">
    <!-- Header Section -->
    <div class="mb-8">
      <h1 class="text-2xl font-semibold text-gray-900 mb-2">Datasets</h1>
      <p class="text-gray-600">Manage your datasets for image labeling</p>
    </div>

    <!-- Create Dataset Section -->
    <div class="mb-8">
      <CreateDatasetModal @refresh="refresh" />
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
                <div class="flex items-baseline gap-2 mb-2">
                  <h2 class="text-lg font-medium">{{ dataset.name }}</h2>
                  <DatasetBadge :training-type="dataset.trainingType" />
                </div>

                <p class="text-sm text-gray-500 mt-1">Updated at{{ formatDate(dataset.createdAt) }}</p>
              </div>
              <UDropdownMenu :items="datasetActions(dataset.id)" @click.stop>
                <UButton color="neutral" variant="ghost" icon="i-heroicons-ellipsis-horizontal-20-solid" />
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
import { computed } from 'vue'
import { useQuery } from '@vue/apollo-composable'
import { gql } from 'graphql-tag'
// import CreateDatasetModal from '@/components/dataset/CreateDatasetModal.vue'

definePageMeta({
  layout: 'default'
})

// TODO: this define twice, can be improved
enum DatasetTrainingType {
    DETECT = 'DETECT',
    SEGMENT = 'SEGMENT'
}

interface Dataset {
  id: string
  name: string
  createdAt: string
  updatedAt: string
  createdBy: string
  images: Image[]
  trainingType: DatasetTrainingType
}

interface Image {
  id: string
}

interface DatasetsQueryResult {
  datasets: Dataset[]
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
      trainingType
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