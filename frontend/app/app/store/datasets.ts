// stores/datasets.ts
import { defineStore } from 'pinia'
import type { Dataset } from '~/types/dataset'
import type { Image } from '~/types/image'

export const useDatasetsStore = defineStore('datasets', () => {
  // --- State ---
  const datasets = ref<Dataset[]>([])
  const currentDatasetId = ref<string | null>(null)

  // Meta information for the current dataset view
  const currentDatasetMeta = ref<{
    images: Image[]
  }>({
    images: [],
  })

  // --- Computed ---
  const currentDataset = computed(() =>
    datasets.value.find(d => d.id === currentDatasetId.value)
  )

  // --- Actions ---
  const setDatasets = (newDatasets: Dataset[]) => {
    datasets.value = newDatasets
  }

  const setCurrentDataset = (datasetId: string | null) => {
    currentDatasetId.value = datasetId
    currentDatasetMeta.value = { images: [] } // Reset meta when switching
  }

  const updateDataset = (datasetId: string, updates: Partial<Dataset>) => {
    const index = datasets.value.findIndex(d => d.id === datasetId)
    if (index !== -1) {
      datasets.value[index] = { ...datasets.value[index], ...updates } as Dataset
    }
  }

  const updateCurrentDatasetMeta = (updates: Partial<typeof currentDatasetMeta.value>) => {
    currentDatasetMeta.value = {
      ...currentDatasetMeta.value,
      ...updates,
    }
  }

  return {
    // State
    datasets: readonly(datasets),
    currentDatasetId: readonly(currentDatasetId),
    currentDatasetMeta,

    // Computed
    currentDataset,

    // Actions
    setDatasets,
    setCurrentDataset,
    updateDataset,
    updateCurrentDatasetMeta,
  }
})
