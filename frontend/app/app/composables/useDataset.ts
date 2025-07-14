// composables/useDataset.ts
import { useQuery } from '@vue/apollo-composable'
import { gql } from 'graphql-tag'
import type { Dataset } from '~/types/dataset'

// GraphQL Queries
const DATASET_QUERY = gql`
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

// Main composable
export const useDataset = (userId: Ref<string | undefined>) => {
  const { result, loading, error, refetch } = useQuery(
    DATASET_QUERY,
    { userId },
    {
      enabled: computed(() => !!userId.value),
    }
  )

  const datasets = computed(() => result.value?.datasets || [])

  return {
    datasets,
    loading,
    error,
    refetch,
  }
}

// Pagination composable
export const useDatasetPagination = (dataset: Ref<Dataset | null>, pageSize = 12) => {
  const currentPage = ref(1)

  const totalImages = computed(() => dataset.value?.images?.length || 0)

  const paginatedImages = computed(() => {
    if (!dataset.value?.images) return []
    const start = (currentPage.value - 1) * pageSize
    return dataset.value.images.slice(start, start + pageSize)
  })

  const resetPagination = () => {
    currentPage.value = 1
  }

  return {
    currentPage,
    pageSize,
    totalImages,
    paginatedImages,
    resetPagination,
  }
}