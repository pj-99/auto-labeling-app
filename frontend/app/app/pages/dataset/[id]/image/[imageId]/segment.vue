<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { useRoute } from 'vue-router'
import { Canvas as FabricCanvas, FabricImage } from 'fabric'
import type {
  LabelSegmentation,
  CustomPolygon,
} from '~/composables/useLabelSeg'
import { useLabelSeg } from '~/composables/useLabelSeg'
import { useSAM } from '~/composables/useSAM'
import AutoLabeling from '~/components/labeling/AutoLabeling.vue'
import type { ModelType } from '~/components/labeling/AutoLabeling.vue'
import type { ClassItem } from '~/components/labeling/ClassPanel.vue'
import ClassPanel from '~/components/labeling/ClassPanel.vue'
import { useClassOptions } from '~/composables/useCalssOptions'
import {
  useAutoLabelingMutation,
  SAM_MUTATION
} from '~/composables/useAutoLabelingQuery'
import LabelList from '~/components/labeling/LabelList.vue'

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

const { mutate: predictSam } = useAutoLabelingMutation(SAM_MUTATION)
const toast = useToast()

// TODO: Replace with actual user ID from auth system
const userId = '123e4567-e89b-12d3-a456-426614174000'

const { 
  image, 
  classes, 
  segmentations,
  refetchClasses,
  refetchSegmentations,
  insertClass 
} = useLabelQueries({ userId, imageId, datasetId })

// Computed properties
const imageWidth = computed(() => image.value?.width)
const classesData = computed(() => ({ classes: classes.value }))
const { classItems, classIdToName } = useClassOptions(classesData)

const wrappedRefetchSegmentations = async () => {
  await refetchSegmentations()
}

// Use label segmentation composable
const {
  startDrawing: startSegDrawing,
  continueDrawing: continueSegDrawing,
  addExistingLabel: addExistingSegmentation,
  handleModification: handleSegModification,
  handleDeletion: handleSegDeletion,
  handleKeyDown: handleSegKeyDown,
  isDrawing: isSegDrawing,
  addPolygon,
} = useLabelSeg(
  fabricCanvas as Ref<FabricCanvas | null>,
  datasetId,
  wrappedRefetchSegmentations,
  imageId,
  selectedClass
)

// Use SAM composable
const {
  samMode,
  isAutoLabelLoading,
  isInSAMEditing,
  handleSAMClick,
  handleSAMKeyboard,
  cleanupSAM,
} = useSAM(
  fabricCanvas as Ref<FabricCanvas | null>,
  selectedClass,
  selectedModel,
  imageWidth,
  addPolygon,
  handleSegModification,
  updatePolygonsSelectability,
  wrappedRefetchSegmentations,
  predictSam,
  toast
)

// Canvas utilities
function updatePolygonsSelectability() {
  if (!fabricCanvas.value) return
  
  const polygons = fabricCanvas.value.getObjects('polygon')
  polygons.forEach((polygon) => {
    polygon.set({
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
  if (drawingMode.value === 'segmentation' && !selectedModel.value) {
    startSegDrawing(e)
  }
}

const handleMouseMove = (e: MouseEvent) => {
  if (drawingMode.value === 'segmentation' && isSegDrawing.value && !selectedModel.value) {
    continueSegDrawing(e)
  }
}

// Combined keyboard event handler
const handleKeyDown = async (e: KeyboardEvent) => {
  // First check SAM keyboard handling
  const handled = await handleSAMKeyboard(e)
  if (handled) return
  
  // Then handle regular segmentation keyboard events
  await handleSegKeyDown(e)
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

  // Add existing segmentation labels
  segmentations.value.forEach((label: LabelSegmentation) => {
    addExistingSegmentation(label)
  })

  // Canvas event handlers
  fabricCanvas.value.on('object:moving', (e) => {
    const obj = e.target as CustomPolygon
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

  // Handle SAM clicks
  fabricCanvas.value.on('mouse:down', async (e) => {
    if (selectedModel.value === 'SAM') {
      await handleSAMClick(
        e.e as MouseEvent,
        image.value!.imageUrl,
        getMousePoint
      )
    }
  })

  fabricCanvas.value.renderAll()
}

// Delete label from list
const deleteSelectedLabel = async (label: { id?: string | number }) => {
  if (!fabricCanvas.value) return

  const objects = fabricCanvas.value.getObjects('polygon')
  const target = objects.find((obj) => {
    const customPolygon = obj as CustomPolygon
    return customPolygon.data?.labelId === label.id
  }) as CustomPolygon | undefined

  if (target) {
    await handleSegDeletion(target)
  }
  await wrappedRefetchSegmentations()
}

// Save modifications
const saveCurrentModifications = async () => {
  if (!fabricCanvas.value) return

  isSaving.value = true
  try {
    const objects = fabricCanvas.value.getObjects('polygon')
    for (const obj of objects) {
      const polygon = obj as CustomPolygon
      if (polygon) {
        await handleSegModification(polygon)
      }
    }
  } finally {
    isSaving.value = false
  }
  await wrappedRefetchSegmentations()
}

const wrappedRefetchClasses = async () => {
  const result = await refetchClasses({ datasetId });
  return result || {};
}

const { 
  newClassName, 
  isAddingClass, 
  createNewClass 
} = useClassManagement({
  insertClass,
  refetchClasses: wrappedRefetchClasses,
  datasetId
})

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
    
    updatePolygonsSelectability()
  }
})

// Watch labels to update canvas
watch(segmentations, (newLabels) => {
  console.log('Labels updated:', newLabels)
  if (!fabricCanvas.value) return
  fabricCanvas.value.getObjects('polygon').forEach((obj) => {
    fabricCanvas.value!.remove(obj)
  })
  newLabels.forEach((label: LabelSegmentation) => {
    addExistingSegmentation(label)
  })
  fabricCanvas.value.renderAll()
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
            icon="i-heroicons-pencil-square"
            :disabled="!selectedClass"
            :color="drawingMode === 'segmentation' ? 'primary' : 'neutral'"
            @click="
              toggleDrawingMode(
                drawingMode === 'segmentation' ? 'none' : 'segmentation'
              )
            "
          >
            {{
              drawingMode === 'segmentation'
                ? 'Exit Polygon Mode'
                : 'Draw Polygon'
            }}
            <template #trailing>
              <span v-if="!selectedClass" class="text-xs"
                >(Select a class first)</span
              >
              <span v-else class="text-xs">
                {{
                  classItems.find((c: ClassItem) => c.value === selectedClass)
                    ?.label
                }}
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
        <LabelList
          :labels="segmentations"
          :class-id-to-name="classIdToName"
          @delete="deleteSelectedLabel"
          @hover="handleLabelHover"
          @select="handleLabelSelect"
        />
      </div>

      <!-- Right Content Area -->
      <div class="flex-1 min-h-[calc(100vh-8rem)] flex flex-col">
        <!-- Image Container -->
        <div
          class="relative flex-1 border-2 rounded-lg flex items-center justify-center overflow-hidden"
          @mousedown="handleMouseDown"
          @mousemove="handleMouseMove"
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
            class="absolute inset-0 flex items-center justify-center z-50"
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