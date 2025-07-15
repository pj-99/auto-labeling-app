<script setup lang="ts">
import { useRoute } from 'vue-router'
import { useDatasetsStore } from '@/store/datasets'
import EmptyStateFallback from '~/components/dataset/EmptyStateFallback.vue'
import FileUploadDropzone from '~/components/dataset/FileUploadDropzone.vue'
import ImageGrid from '~/components/dataset/ImageGrid.vue'
import { useLabelQuery } from '~/composables/useLabelMap'
import SearchModal from '~/components/dataset/SearchModal.vue'
import { useUserStore } from '~/store/user'



const route = useRoute()
const datasetId = route.params.id

const toast = useToast()
const datasetsStore = useDatasetsStore()
const { uploading, uploadImages } = useImageUpload()
const userStore = useUserStore()
const userId = computed(() => userStore.userId)


// Accepted image file types
const acceptedImageTypes = ['image/jpeg', 'image/jpg', 'image/png']
const acceptedExtensions = '.jpg,.jpeg,.png'

const { fetchLabelsWithClassNames } = useLabelQuery()
const { dataset, loading, refetch } = useSingleDataset(datasetId as string, userId)

const isSearchModalOpen = ref(false)

const openSearchModal = () => {
  isSearchModalOpen.value = true
}


// Stores labels of any type (Detection or Segmentation)
const imageLabelsMap = ref<Map<string, LabelDetection[] | LabelSegmentation[]>>(new Map())

// Format timestamp to readable date string
const formatDate = (dateString: string) => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })
}

// Handle selected files
const processFiles = async (files: FileList | File[]) => {
  await uploadImages(files, datasetId as string, userId.value, () => {
    refetch()
  })
}

// Dataset pagination
const { currentPage, pageSize, totalImages, paginatedImages } = useDatasetPagination(dataset)

// Fetch labels for a given image
const fetchLabelsForImage = async (imageId: string) => {
  if (!dataset.value) return

  try {
    const labels = await fetchLabelsWithClassNames(
      dataset.value.id,
      imageId,
      dataset.value.trainingType
    )
    imageLabelsMap.value.set(imageId, labels as LabelDetection[] | LabelSegmentation[])
  } catch (error) {
    console.error(`Failed to fetch labels for image ${imageId}:`, error)
  }
}

// Lifecycle: on mount
onMounted(async () => {
  datasetsStore.setCurrentDataset(route.params.id as string)

  if (!loading.value && dataset.value && paginatedImages.value) {
    datasetsStore.updateCurrentDatasetMeta({ images: paginatedImages.value })

    for (const image of paginatedImages.value) {
      if (!imageLabelsMap.value.has(image.id)) {
        await fetchLabelsForImage(image.id)
      }
    }
  }
})

// Cleanup on unmount
onUnmounted(() => {
  datasetsStore.setCurrentDataset(null)
})

// Watch dataset and pagination changes
watch(
  [dataset, currentPage, loading],
  ([currentDataset, _, isLoading]) => {
    if (!isLoading && currentDataset) {
      datasetsStore.updateCurrentDatasetMeta({ images: paginatedImages.value })
    }
  },
  { immediate: true }
)

// Watch paginated images and fetch labels
watch(paginatedImages, async (images) => {
  if (!dataset.value) return

  for (const image of images) {
    if (!imageLabelsMap.value.has(image.id)) {
      await fetchLabelsForImage(image.id)
    }
  }
})

// Handle file validation error
const handleValidationError = (invalidFiles: File[]) => {
  toast.add({
    title: 'Invalid file type',
    description: `The following files are not supported image formats: ${invalidFiles
      .map((f) => f.name)
      .join(', ')}`,
    color: 'error',
    duration: 5000,
    icon: 'i-heroicons-exclamation-triangle',
  })
}

const collapsible = ref(false)

const toggleCollapsible = () => {
  collapsible.value = !collapsible.value
}
</script>

<template>
  <div class="mx-auto sm:px-6 lg:px-8">
    <!-- Header Section -->
    <div class="mb-8">
    <UCard class="mb-4">
      <template #header>
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-2xl font-semibold">{{ dataset?.name }}</h1>
            <p class="text-muted text-sm">Upload and manage images in this dataset</p>
          </div>
          <DatasetBadge :training-type="dataset?.trainingType" />
        </div>
      </template>

        <div class="flex flex-wrap items-center gap-3">
          <UBadge variant="soft" size="md">
            {{ dataset?.images?.length || 0 }} images
          </UBadge>
          <UBadge variant="outline" size="md">
            Created {{ formatDate(dataset?.createdAt) }}
          </UBadge>
        </div>
    </UCard>
      <!-- Image Searching Button -->
      <div class="mt-2 flex gap-4">
        <UButton
          label="Image Searching (WIP)"
          icon="i-heroicons-magnifying-glass"
          color="secondary"
          variant="outline"
          class="flex-1"
          disabled
          size="lg"
          @click="openSearchModal"
        />

        <UButton
          label="Upload Images"
          color="primary"
          variant="subtle"
          class="flex-1"
          icon="i-heroicons-arrow-up-on-square"
          trailing-icon="i-lucide-chevron-down"
          @click="toggleCollapsible"
        />
      </div>

      

      <!-- Upload Section -->
      <UCollapsible 
      v-model:open="collapsible"
      class="flex flex-col" 
      >
        <template #content>
          <div class="mb-12 mt-4">
            <FileUploadDropzone
              :loading="uploading"
              :accept="acceptedExtensions"
              :accepted-types="acceptedImageTypes"
              @files-selected="processFiles"
              @validation-error="handleValidationError"
            />
          </div>
        </template>
      </UCollapsible>

      <!-- Image Grid Section -->
      <div class="mt-6 mb-12">
        <h2 class="text-xl font-medium mb-4">Dataset Images</h2>

        <!-- Pagination -->
        <div v-if="totalImages > pageSize" class="my-8 flex justify-center">
          <UPagination
            v-model:page="currentPage"
            :total="totalImages"
            :items-per-page="pageSize"
            show-first
            show-last
          />
        </div>

        <div v-if="loading" class="text-center py-8">
          <p class="text-gray-600">Loading images...</p>
        </div>

        <div v-else>
          <ImageGrid
            v-if="!loading && paginatedImages.length > 0"
            :images="paginatedImages"
            :labels="imageLabelsMap"
            :dataset-id="datasetId?.toString() || ''"
            :training-type="dataset.trainingType"
          />
        </div>

        <EmptyStateFallback
          v-if="!loading && (!dataset?.images || dataset.images.length === 0)"
          title="Dataset is empty"
          description="Images will appear here once uploaded"
          icon="i-heroicons-cube-transparent"
        />
        <SearchModal v-model:open="isSearchModalOpen" />
      </div>
    </div>
  </div>
</template>
