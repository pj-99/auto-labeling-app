<script setup lang="ts">
interface Props {
  accept?: string
  acceptedTypes?: string[]
  multiple?: boolean
  loading?: boolean
  disabled?: boolean
  icon?: string
  title?: string
  dragTitle?: string
  description?: string
  acceptDescription?: string
  buttonText?: string
  loadingText?: string
}

const props = withDefaults(defineProps<Props>(), {
  accept: '.jpg,.jpeg,.png',
  acceptedTypes: () => ['image/jpeg', 'image/jpg', 'image/png'],
  multiple: true,
  loading: false,
  disabled: false,
  icon: 'i-heroicons-cloud-arrow-up',
  title: 'Drop Files Here',
  dragTitle: 'Release to Upload Files',
  description: 'Drag and drop your files here, or click to select files',
  acceptDescription: 'Supported formats: JPG, PNG',
  buttonText: 'Select Files',
  loadingText: 'Uploading...'
})

const emit = defineEmits<{
  'files-selected': [files: FileList | File[]]
  'validation-error': [invalidFiles: File[]]
}>()

const fileInput = ref<HTMLInputElement | null>(null)
const isDragging = ref(false)

// Validate file type
const isValidFile = (file: File): boolean => {
  return props.acceptedTypes.includes(file.type)
}

// Process files with validation
const processFiles = (files: FileList | File[]) => {
  const fileArray = Array.from(files)
  
  // Validate all files first
  const invalidFiles = fileArray.filter(file => !isValidFile(file))
  if (invalidFiles.length > 0) {
    emit('validation-error', invalidFiles)
    return
  }

  emit('files-selected', files)
}

const handleFileChange = (event: Event) => {
  const input = event.target as HTMLInputElement
  if (!input.files?.length) return
  
  processFiles(input.files)
  
  // Reset input
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

const handleUploadClick = () => {
  fileInput.value?.click()
}

// Drag and drop handlers
const handleDragOver = (e: DragEvent) => {
  e.preventDefault()
  if (!props.disabled && !props.loading) {
    isDragging.value = true
  }
}

const handleDragLeave = (e: DragEvent) => {
  e.preventDefault()
  isDragging.value = false
}

const handleDrop = (e: DragEvent) => {
  e.preventDefault()
  isDragging.value = false
  
  if (props.disabled || props.loading) return
  if (!e.dataTransfer?.files?.length) return
  
  processFiles(e.dataTransfer.files)
}
</script>

<template>
  <div
    class="border-2 border-dashed rounded-lg p-8 transition-all duration-200"
    :class="{
      'border-primary-500 bg-primary-50 dark:bg-primary-950': isDragging && !disabled,
      'border-gray-300 dark:border-gray-700': !isDragging || disabled,
      'opacity-50 cursor-not-allowed': disabled
    }"
    @dragover="handleDragOver"
    @dragleave="handleDragLeave"
    @drop="handleDrop"
  >
    <div class="text-center">
      <UIcon
        :name="icon"
        class="mx-auto h-12 w-12 transition-colors duration-200"
        :class="{
          'text-primary-500': isDragging && !disabled,
          'text-gray-400': !isDragging || disabled
        }"
      />
      <div class="mt-4">
        <h3 class="text-lg font-semibold">
          {{ isDragging ? dragTitle : title }}
        </h3>
        <p class="mt-1 text-sm">
          {{ description }}
        </p>
        <p v-if="acceptDescription" class="mt-2 text-xs text-gray-500">
          {{ acceptDescription }}
        </p>
      </div>
      
      <slot name="button">
        <UButton
          class="mt-4"
          :loading="loading"
          :disabled="disabled || loading"
          @click="handleUploadClick"
        >
          {{ loading ? loadingText : buttonText }}
        </UButton>
      </slot>
      
      <input
        ref="fileInput"
        type="file"
        :multiple="multiple"
        :accept="accept"
        :disabled="disabled || loading"
        class="hidden"
        @change="handleFileChange"
      >
    </div>
  </div>
</template>