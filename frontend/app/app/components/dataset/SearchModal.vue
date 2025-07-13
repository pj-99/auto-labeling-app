<script setup lang="ts">
import { ref, computed } from 'vue'
import FileUploadDropzone from '@/components/dataset/FileUploadDropzone.vue'

const toast = useToast()

const props = defineProps<{ open: boolean }>()
const emit = defineEmits<{ 'update:open': [value: boolean] }>()

const isOpen = computed({
  get: () => props.open,
  set: (value) => emit('update:open', value)
})

const collapsible = ref(false)
const toggleCollapsible = () => {
  collapsible.value = !collapsible.value
}

const uploading = ref(false)
const acceptedExtensions = '.jpg,.jpeg,.png'
const acceptedImageTypes = ['image/jpeg', 'image/png']

const searchQuery = ref('')
const isSearching = ref(false)
const searchResults = ref<string[]>([])
const selectedImages = ref<string[]>([])

const handleValidationError = (invalidFiles: File[]) => {
  toast.add({
    title: 'Invalid file type',
    description: `These files are not supported: ${invalidFiles.map(f => f.name).join(', ')}`,
    color: 'error',
    icon: 'i-heroicons-exclamation-triangle',
    duration: 5000
  })
}

const processFiles = (files: File[] | FileList) => {
  const fileArray = Array.from(files)
  if (fileArray.length > 1) {
    toast.add({
      title: 'Multiple images detected',
      description: 'Only the first image will be used for visual search.',
      color: 'warning',
      icon: 'i-heroicons-exclamation-triangle',
      duration: 4000
    })
  }

  const firstFile = fileArray[0]
  if (!firstFile) return

  uploading.value = true
  setTimeout(() => {
    console.log('Files selected:', firstFile.name)
    uploading.value = false
    isOpen.value = false
  }, 1000)
}

const doSearch = async () => {
  if (!searchQuery.value.trim()) return

  isSearching.value = true
  searchResults.value = []
  selectedImages.value = []

  await new Promise(resolve => setTimeout(resolve, 1000))

// Generate random imgur-like URLs for demo search results
const randomImgurIds = Array.from({ length: 16 }, () => 
    Math.floor(100000 + Math.random() * 900000).toString(16)
)
searchResults.value = randomImgurIds.map(id => `https://i.imgur.com/${id}.jpg`)

  isSearching.value = false
}

const toggleSelection = (url: string) => {
  if (selectedImages.value.includes(url)) {
    selectedImages.value = selectedImages.value.filter(img => img !== url)
  } else {
    selectedImages.value.push(url)
  }
}

const handleAddToDataset = () => {
  console.log('Added to dataset:', selectedImages.value)
  toast.add({
    title: 'Images added',
    description: `${selectedImages.value.length} image(s) added to dataset.`,
    color: 'primary',
    icon: 'i-heroicons-check-circle',
  })
  selectedImages.value = []
  isOpen.value = false
}

// Watch isOpen to reset state when modal closes
watch(isOpen, (value) => {
    if (!value) {
        searchQuery.value = ''
        searchResults.value = []
        selectedImages.value = []
        collapsible.value = false
    }
})
</script>

<template>
  <UModal
    v-model:open="isOpen"
    title="Search Images"
    :ui="{
      content: 'min-w-[70vw] min-h-[80vh] overflow-auto rounded-lg shadow-lg ring ring-default'
    }"
  >
    <template #body>
      <!-- 🔹 Row: Text Search + Toggle -->
      <div class="mt-2 flex gap-4">
        <UInput
          v-model="searchQuery"
          icon="i-heroicons-magnifying-glass"
          placeholder="Search by filename or label..."
          class="flex-1"
          :disabled="isSearching"
          @keydown.enter="doSearch"
        />

        <UButton
          label="Image Search"
          icon="i-heroicons-photo"
          color="primary"
          variant="soft"
          trailing-icon="i-lucide-chevron-down"
          :loading="isSearching"
          :disabled="isSearching"
          @click="toggleCollapsible"
        />
      </div>

      <!-- 🔹 Dropzone Section -->
      <UCollapsible v-model:open="collapsible" class="flex flex-col">
        <template #content>
          <div class="space-y-4 mt-4">
            <FileUploadDropzone
              :loading="uploading"
              :accept="acceptedExtensions"
              :accepted-types="acceptedImageTypes"
              :multiple="false"
              @files-selected="processFiles"
              @validation-error="handleValidationError"
            />
            <p class="text-xs text-muted mt-2">
              Upload a single image to find visually similar results.
            </p>
          </div>
        </template>
      </UCollapsible>

      <!-- 🔹 Result Grid -->
      <div class="mt-6 grid grid-cols-4 gap-3 min-h-[200px]">
        <template v-if="isSearching">
          <USkeleton
            v-for="i in 16"
            :key="i"
            class="aspect-square w-full rounded"
          />
        </template>

        <template v-else>
          <div
            v-for="img in searchResults"
            :key="img"
            class="relative cursor-pointer rounded overflow-hidden aspect-square"
            :class="[
            'transition-all duration-150',
            selectedImages.includes(img)
                ? 'ring-4 ring-primary'
                : 'hover:ring-2 hover:ring-gray-300 hover:ring-offset-2'
            ]"
            @click="toggleSelection(img)"
          >
            <NuxtImg 
                :src="img" 
                class="w-full h-full object-cover select-none"
                loading="lazy"
                placeholder
            />
          </div>
        </template>
      </div>
    </template>

    <!-- 🔹 Footer Action -->
    <template v-if="selectedImages.length > 0" #footer>
      <div class="mt-6 flex justify-end gap-2">
        <UButton
          color="primary"
          icon="i-heroicons-plus"
          :label="`Add ${selectedImages.length} image(s) to dataset`"
          @click="handleAddToDataset"
        />
        <UButton
        label="reset"
        color="neutral"
        variant="outline" 
        icon="i-heroicons-x-mark"
        @click="selectedImages = []"
        />
      </div>
    </template>
  </UModal>
</template>