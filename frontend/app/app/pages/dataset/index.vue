
<script setup lang="ts">
import CreateDatasetModal from '@/components/dataset/CreateDatasetModal.vue'
import { useDatasetsStore } from '@/store/datasets'
import { useUserStore } from '~/store/user'
import { useDataset } from '~/composables/useDataset'

const datasetsStore = useDatasetsStore()
const userStore = useUserStore()
const userId = computed(() => userStore.userId)

definePageMeta({
  layout: 'default',
})

const {
  datasets: datasetsData,
  loading: datasetsLoading,
  refetch,
} = useDataset(userId)

const datasets = computed(() => datasetsData.value || [])

watch(datasetsData, (newDatasets) => {
  if (newDatasets) {
    datasetsStore.setDatasets(newDatasets)
  }
}, { immediate: true })

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleString()
}

const datasetActions = (datasetId: string) => [
  [
    {
      label: 'Edit',
      icon: 'i-heroicons-pencil-square',
      click: () => {
        // TODO: Implement edit functionality
        console.log('Edit dataset:', datasetId)
      },
    },
    {
      label: 'Delete',
      icon: 'i-heroicons-trash',
      click: () => {
        // TODO: Implement delete functionality
        console.log('Delete dataset:', datasetId)
      },
    },
  ],
]
</script>


<template>
  <div class="max-w-3xl mx-auto sm:px-6 lg:px-8">
    <!-- Header Section -->
    <div class="mb-8">
      <h1 class="text-2xl font-semibold text-gray-900 mb-2">Datasets</h1>
      <p class="text-gray-600">Manage your datasets for image labeling</p>
    </div>

    <!-- Create Dataset Section -->
    <div class="mb-8">
      <CreateDatasetModal @refresh="refetch" />
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
        <UCard
          v-for="dataset in datasets"
          :key="dataset.updatedAt"
          class="hover:shadow-md transition-shadow cursor-pointer"
        >
          <NuxtLink :to="`/dataset/${dataset.id}`" class="block">
            <div class="flex items-start justify-between">
              <div>
                <div class="flex items-baseline gap-2 mb-2">
                  <h2 class="text-lg font-medium">{{ dataset.name }}</h2>
                  <DatasetBadge :training-type="dataset.trainingType" />
                </div>

                <p class="text-sm text-gray-500 mt-1">
                  Updated {{ formatDate(dataset.createdAt) }}
                </p>
              </div>
              <UDropdownMenu :items="datasetActions(dataset.id)" @click.stop>
                <UButton
                  color="neutral"
                  variant="ghost"
                  icon="i-heroicons-ellipsis-horizontal-20-solid"
                />
              </UDropdownMenu>
            </div>
            <div class="mt-4">
              <p class="text-sm text-gray-600">
                {{ dataset.images?.length || 0 }} images
              </p>
            </div>
          </NuxtLink>
        </UCard>

        <!-- Empty State -->
        <div
          v-if="!datasetsLoading && datasets.length === 0"
          class="text-center py-4"
        >
          <p class="text-gray-600">
            No datasets found. Create one above to get started.
          </p>
        </div>
      </div>
    </div>
  </div>
</template>