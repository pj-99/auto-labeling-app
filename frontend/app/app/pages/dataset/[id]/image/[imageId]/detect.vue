<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useQuery, useMutation } from '@vue/apollo-composable'
import { gql } from 'graphql-tag'
import { Canvas as FabricCanvas, FabricImage } from 'fabric'
import { useLabel } from '~/composables/useLabel'
import { useSAMBbox } from '~/composables/useSAMBox'
import type {
  LabelDetection,
  CustomRect,
} from '~/composables/useLabel'
import type { Ref } from 'vue'
import AutoLabeling from '~/components/labeling/AutoLabeling.vue'
import type { ModelType } from '~/components/labeling/AutoLabeling.vue'
import { useClassOptions } from '~/composables/useCalssOptions'
import ClassPanel from '~/components/labeling/ClassPanel.vue'
import {
  useAutoLabelingMutation,
  SAMMutation,
} from '~/composables/useAutoLabelingQuery'

const route = useRoute()

const imageIdBase64 = route.params.imageId
const imageId = decodeBase64ToUuid(imageIdBase64 as string)
const datasetId = decodeBase64ToUuid(route.params.id as string)

const selectedModel = ref<ModelType | null>(null)
const canvasEl = ref<HTMLCanvasElement | null>(null)
const fabricCanvas = ref<FabricCanvas | null>(null)
const drawingMode = ref<'none' | 'box' | 'segmentation'>('none')
const isSaving = ref(false)
const selectedClass = ref<number | undefined>(undefined)
const newClassName = ref('')
const isAddingClass = ref(false)

const { mutate: predictSam } = useAutoLabelingMutation(SAMMutation)
const toast = useToast()

// TODO: Replace with actual user ID from auth system
const userId = '123e4567-e89b-12d3-a456-426614174000'

// GraphQL Queries
const IMAGE_QUERY = gql`
  query GetImage($userId: UUID!, $imageId: UUID!) {
    image(userId: $userId, imageId: $imageId) {
      id
      imageName
      imageUrl
      width
      height
      createdAt
      updatedAt
      caption
      createdBy
    }
  }
`

const LABEL_DETECTIONS_QUERY = gql`
  query GetLabelDetections($datasetId: UUID!, $imageId: UUID!) {
    labelDetections(datasetId: $datasetId, imageId: $imageId) {
      id
      classId
      xCenter
      yCenter
      width
      height
    }
  }
`

const CLASSES_QUERY = gql`
  query GetClasses($datasetId: UUID!) {
    classes(datasetId: $datasetId) {
      id
      name
      createdAt
      updatedAt
    }
  }
`

const INSERT_CLASS_MUTATION = gql`
  mutation InsertClass($datasetId: UUID!, $name: String!) {
    insertClass(datasetId: $datasetId, name: $name) {
      id
      name
      createdAt
      updatedAt
    }
  }
`

// Query hooks
const { result: imageData } = useQuery(IMAGE_QUERY, {
  userId,
  imageId,
})

const { result: labelData, refetch: refetchLabels } = useQuery(
  LABEL_DETECTIONS_QUERY,
  {
    datasetId,
    imageId,
  }
)

const { result: classesData, refetch: refetchClasses } = useQuery(
  CLASSES_QUERY,
  {
    datasetId,
  }
)

const { mutate: insertClass } = useMutation(INSERT_CLASS_MUTATION)

// Computed properties
const image = computed(() => imageData.value?.image)
const labels = computed(() => labelData.value?.labelDetections || [])
const imageWidth = computed(() => image.value?.width)

const { classItems, classIdToName } = useClassOptions(classesData)

const wrappedRefetchLabels = async () => {
  await refetchLabels()
}

// Use label composable
const {
  startDrawing: startBoxDrawing,
  continueDrawing: continueBoxDrawing,
  finishDrawing: finishBoxDrawing,
  addExistingLabel: addExistingBox,
  handleModification: handleBoxModification,
  handleDeletion: handleBoxDeletion,
  isDrawing: isBoxDrawing,
} = useLabel(
  fabricCanvas as Ref<FabricCanvas | null>,
  datasetId,
  wrappedRefetchLabels,
  imageId,
  selectedClass
)

// Use SAM Bbox composable
const {
  samMode,
  isAutoLabelLoading,
  isInSAMEditing,
  handleSAMClick,
  handleSAMKeyboard,
  cleanupSAM,
} = useSAMBbox(
  fabricCanvas as Ref<FabricCanvas | null>,
  selectedClass,
  selectedModel as Ref<string>,
  imageWidth,
  addExistingBox,
  handleBoxModification,
  updateBoxesSelectability,
  wrappedRefetchLabels,
  predictSam,
  (xyxy, width, height) => {
    const dimensions = xyxyToXCenterYCenter(xyxy, width, height);
    return { ...dimensions, classId: selectedClass.value || 0 };
  },
  toast
)

// Canvas utilities
function updateBoxesSelectability() {
  if (!fabricCanvas.value) return
  
  const rects = fabricCanvas.value.getObjects('rect')
  rects.forEach((rect) => {
    rect.set({
      selectable: !selectedModel.value,
      evented: !selectedModel.value,
      hoverCursor: selectedModel.value ? 'crosshair' : 'move'
    })
  })
  fabricCanvas.value.renderAll()
}

// Drawing mode toggle
const toggleDrawingMode = (mode: 'none' | 'box' | 'segmentation') => {
  drawingMode.value = mode
  if (!fabricCanvas.value) return
}

// Mouse event handlers
const handleMouseDown = (e: MouseEvent) => {
  if (drawingMode.value === 'box' && !selectedModel.value) {
    startBoxDrawing(e)
  }
}

const handleMouseMove = (e: MouseEvent) => {
  if (drawingMode.value === 'box' && isBoxDrawing.value && !selectedModel.value) {
    continueBoxDrawing(e)
  }
}

const handleMouseUp = async () => {
  if (drawingMode.value === 'box' && isBoxDrawing.value && !selectedModel.value) {
    
    await finishBoxDrawing()

    updateBoxesSelectability()

  }
}

// Combined keyboard event handler
const handleKeyDown = async (e: KeyboardEvent) => {
  // First check SAM keyboard handling
  const handled = await handleSAMKeyboard(e)
  if (handled) return
  // Then handle regular box keyboard events
    if (e.key === 'Backspace' || e.key === 'Delete') {
      if (!fabricCanvas.value) return
      const activeObject = fabricCanvas.value.getActiveObject()
      if (activeObject && 'data' in activeObject) {
        const rect = activeObject as CustomRect
        await handleBoxDeletion(rect)
        fabricCanvas.value.remove(rect)
        fabricCanvas.value.renderAll()
        await wrappedRefetchLabels()
      }
  }
}

// Initialize canvas
const initCanvas = async () => {
  if (!image.value || !canvasEl.value) return

  // Clean up existing canvas if it exists
  if (fabricCanvas.value) {
    fabricCanvas.value.dispose()
    fabricCanvas.value = null
  }

  // Load main image first to get its dimensions
  const img = await FabricImage.fromURL(image.value.imageUrl)

  // Get the original image dimensions
  const imageWidth = img.width
  const imageHeight = img.height
  const imageAspectRatio = imageWidth / imageHeight

  // Get the container dimensions
  const containerWidth = canvasEl.value.parentElement?.clientWidth || 800
  const containerHeight = canvasEl.value.parentElement?.clientHeight || 600

  // Calculate canvas dimensions to fit within container while maintaining image aspect ratio
  let canvasWidth, canvasHeight

  if (containerWidth / containerHeight > imageAspectRatio) {
    canvasHeight = containerHeight
    canvasWidth = containerHeight * imageAspectRatio
  } else {
    canvasWidth = containerWidth
    canvasHeight = containerWidth / imageAspectRatio
  }

  // Initialize Fabric.js canvas with calculated dimensions
  fabricCanvas.value = new FabricCanvas(canvasEl.value, {
    width: canvasWidth,
    height: canvasHeight,
    uniformScaling: false,
    selection: false,
  })

  // Scale image to fit the canvas
  img.scaleToWidth(canvasWidth)

  // Add image to canvas
  fabricCanvas.value.add(markRaw(img))
  
  // Centering
  img.set({
    left: fabricCanvas.value.width! / 2,
    top: fabricCanvas.value.height! / 2,
    originX: 'center',
    originY: 'center',
    selectable: false,
    evented: false,
  })

  // Add existing bounding box labels
  labels.value.forEach((label: LabelDetection) => {
    addExistingBox(label)
  })

  // Canvas event handlers
  fabricCanvas.value.on('object:moving', (e) => {
    if (drawingMode.value != 'box') return

    const obj = e.target as CustomRect
    // Bounded in canvas
    if (obj.left! < 0) {
      obj.left = 0
    } else if (obj.left! + obj.width! > fabricCanvas.value!.width!) {
      obj.left = fabricCanvas.value!.width! - obj.width!
    }

    if (obj.top! < 0) {
      obj.top = 0
    } else if (obj.top! + obj.height! > fabricCanvas.value!.height!) {
      obj.top = fabricCanvas.value!.height! - obj.height!
    }
  })

  // Handle object modifications
  fabricCanvas.value.on('object:modified', async (e) => {
    const obj = e.target
    if (!obj || !('data' in obj)) return

    if ('width' in obj) {
      await handleBoxModification(obj as CustomRect)
    }
  })

  // Handle SAM clicks
  fabricCanvas.value.on('mouse:down', async (e) => {
    if (selectedModel.value === 'SAM' && image.value) {
      await handleSAMClick(
        e.e as MouseEvent,
        image.value.imageUrl,
        image.value.width,
        image.value.height,
        getMousePoint
      )
    }
  })

  fabricCanvas.value.renderAll()
}

// Delete label from list
const deleteSelectedLabel = async (label: LabelDetection) => {
  if (!fabricCanvas.value) return

  const objects = fabricCanvas.value.getObjects('rect')
  const rect = objects.find((obj) => {
    const customRect = obj as CustomRect
    return customRect.data?.labelId === label.id
  }) as CustomRect | undefined

  if (rect) {
    await handleBoxDeletion(rect)
    fabricCanvas.value.remove(rect)
    fabricCanvas.value.renderAll()
  }
  await wrappedRefetchLabels()
}

// Save modifications
const saveCurrentModifications = async () => {
  if (!fabricCanvas.value) return

  isSaving.value = true
  try {
    const objects = fabricCanvas.value.getObjects('rect')
    for (const obj of objects) {
      const rect = obj as CustomRect
      if (rect) {
        await handleBoxModification(rect)
      }
    }
  } finally {
    isSaving.value = false
    await wrappedRefetchLabels()
  }
}

// Create new class
const createNewClass = async () => {
  if (!newClassName.value) return

  isAddingClass.value = true
  try {
    await insertClass({
      datasetId,
      name: newClassName.value,
    })
    newClassName.value = ''
    await refetchClasses()
  } catch (error) {
    console.error('Failed to create class:', error)
  } finally {
    isAddingClass.value = false
  }
}

// Lifecycle hooks
onMounted(async () => {
  await nextTick()
  if (image.value) {
    initCanvas()
    window.addEventListener('keydown', handleKeyDown)
  }
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeyDown)
  if (fabricCanvas.value) {
    fabricCanvas.value.dispose()
    fabricCanvas.value = null
  }
})

// Watchers
watch(
  () => image.value?.imageUrl,
  async (newUrl, oldUrl) => {
    if (newUrl && newUrl !== oldUrl) {
      if (fabricCanvas.value) {
        fabricCanvas.value.dispose()
        fabricCanvas.value = null
      }
      initCanvas()
    }
  },
  { immediate: true }
)

watch(selectedModel, (newModel, oldModel) => {
  if (fabricCanvas.value) {
    // Clean up SAM if switching away
    if (oldModel === 'SAM') {
      cleanupSAM()
    }
    
    fabricCanvas.value.defaultCursor = newModel ? 'crosshair' : 'default'
    
    if (newModel) {
      fabricCanvas.value.discardActiveObject()
    }
    
    updateBoxesSelectability()
  }
})

// Watch drawingMode
watch(drawingMode, (newMode) => {
  if (fabricCanvas.value) {
    if (newMode === 'box') {
      fabricCanvas.value.defaultCursor = 'crosshair'
    } else {
      fabricCanvas.value.defaultCursor = 'default'
    }
  }
})
</script>

<template>
  <div class="w-full p-12">
    <!-- Main Content -->
    <div class="mx-auto flex gap-8">
      <!-- Left Sidebar -->
      <div
        class="w-48 shrink-0 flex flex-col gap-6 rounded-lg shadow-lg border p-4 h-fit"
      >
        <AutoLabeling 
          v-model="selectedModel" 
          v-model:sam-mode="samMode"
          class="w-full" 
        />

        <ClassPanel
          v-model:selected-class="selectedClass"
          v-model:new-class-name="newClassName"
          :class-items="classItems"
          :is-adding-class="isAddingClass"
          :create-new-class="createNewClass"
        />

        <div class="flex flex-col gap-2">
          <UButton
            icon="i-heroicons-square-2-stack"
            :disabled="!selectedClass"
            :color="drawingMode === 'box' ? 'primary' : 'neutral'"
            @click="toggleDrawingMode(drawingMode === 'box' ? 'none' : 'box')"
          >
            {{ drawingMode === 'box' ? 'Exit Box Mode' : 'Draw Box' }}
            <template #trailing>
              <span v-if="!selectedClass" class="text-xs text-gray-500"
                >(Select a class first)</span
              >
              <span v-else class="text-xs">
                {{ classIdToName.get(selectedClass!) }}
              </span>
            </template>
          </UButton>
        </div>

        <UButton
          icon="i-heroicons-check-circle"
          color="primary"
          :loading="isSaving"
          @click="saveCurrentModifications"
        >
          Save Changes
        </UButton>

        <!-- Label List -->
        <div class="flex flex-col gap-2">
          <h2 class="text-lg font-medium mb-2">Label List</h2>
          <div class="space-y-2 max-h-[calc(100vh-36rem)] overflow-y-auto">
            <div v-if="labels.length === 0" class="text-gray-500 text-sm">
              No labels yet
            </div>
            <div
              v-for="label in labels"
              :key="label.id"
              class="flex items-center justify-between p-2 rounded-lg"
            >
              <div class="flex items-center gap-2">
                <div
                  class="w-2 h-2 rounded-full"
                  :style="{ backgroundColor: getClassColor(label.classId) }"
                />
                <span class="text-sm">{{
                  classIdToName.get(label.classId) || `Class ${label.classId}`
                }}</span>
              </div>
              <UButton
                icon="i-heroicons-trash"
                color="error"
                variant="ghost"
                size="xs"
                @click="deleteSelectedLabel(label)"
              />
            </div>
          </div>
        </div>
      </div>

      <!-- Right Content Area -->
      <div class="flex-1 min-h-[calc(100vh-8rem)] flex flex-col">
        <!-- Image Container -->
        <div
          class="relative flex-1 border-2 rounded-lg flex items-center justify-center overflow-hidden"
          @mousedown="handleMouseDown"
          @mousemove="handleMouseMove"
          @mouseup="handleMouseUp"
        >
          <!-- SAM Mode Indicator -->
          <div v-if="isInSAMEditing" class="absolute top-4 left-4 z-10 bg-orange-500 text-white px-3 py-2 rounded-lg shadow-lg">
            <div class="flex items-center gap-2">
              <UIcon name="i-heroicons-cursor-arrow-rays" />
              <span>Click to {{ samMode === 'add' ? 'add' : 'remove' }} points</span>
            </div>
            <div class="text-sm mt-1">
              Press <kbd class="px-1 bg-orange-600 rounded">Enter</kbd> to confirm or 
              <kbd class="px-1 bg-orange-600 rounded">ESC</kbd> to cancel
            </div>
          </div>

          <!-- Loading Overlay for Auto-Labeling -->
          <div
            v-if="isAutoLabelLoading"
            class="absolute inset-0 bg-black/50 dark:bg-black/70 flex items-center justify-center z-50"
          >
            <div class="rounded-lg p-4 flex flex-col items-center gap-2">
              <span class="text-sm font-medium">Auto-labeling...</span>
              <UProgress color="success" />
            </div>
          </div>
          
          <canvas ref="canvasEl" class="absolute inset-0" />
          
          <div v-if="!image" class="flex flex-col items-center gap-2">
            <UIcon name="i-heroicons-photo" class="w-16 h-16" />
            <span>No image selected</span>
          </div>
        </div>

        <!-- Image Info -->
        <div class="mt-4">
          <h3 class="text-lg font-medium">
            {{ image?.imageName || 'Mountain View' }}
          </h3>
          <div class="h-0.5 w-24 mt-2" />
        </div>
      </div>
    </div>
  </div>
</template>