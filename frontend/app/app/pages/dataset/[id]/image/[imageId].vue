<template>
    <div class="w-full p-12">
        <!-- Main Content -->
        <div class="mx-auto flex gap-8">
            <!-- Left Sidebar -->
            <div class="w-48 flex flex-col gap-6">
                <UButton icon="i-heroicons-sparkles" color="neutral">
                    Auto Labeling
                </UButton>
                <UButton icon="i-heroicons-pencil-square" @click="toggleDrawingMode(!isDrawingMode)">
                    {{ isDrawingMode ? 'Exit Drawing Mode' : 'Draw A Box' }}
                </UButton>

                <!-- Label List -->
                <div class="flex flex-col gap-2">
                    <h2 class="text-lg font-medium mb-2">Label List</h2>
                    <div class="space-y-2">
                        <div v-if="labels.length === 0" class="text-gray-500 text-sm">
                            No labels yet
                        </div>
                        <div
v-for="label in labels" :key="label.id" 
                            class="flex items-center justify-between p-2 bg-gray-50 rounded-lg hover:bg-gray-100">
                            <div class="flex items-center gap-2">
                                <div class="w-2 h-2 rounded-full bg-blue-500"/>
                                <span class="text-sm">Class {{ label.classId }}</span>
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
            <div class="flex-1 min-h-[calc(100vh-8rem)]">
                <!-- Image Container -->
                <div
                    class="relative w-full h-[calc(100vh-12rem)] border-2 border-gray-300 rounded-lg bg-gray-50 flex items-center justify-center"
                    @mousedown="handleMouseDown"
                    @mousemove="handleMouseMove"
                    @mouseup="handleMouseUp">
                    <canvas ref="canvasEl" class="absolute inset-0" />
                    <div v-if="!image" class="text-gray-400 flex flex-col items-center gap-2">
                        <UIcon name="i-heroicons-photo" class="w-16 h-16" />
                        <span>No image selected</span>
                    </div>
                </div>

                <!-- Image Info -->
                <div class="mt-4">
                    <h3 class="text-lg font-medium">{{ image?.imageName || 'Mountain View' }}</h3>
                    <div class="h-0.5 w-24 bg-gray-300 mt-2"/>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue';
import { useRoute } from 'vue-router'
import { useQuery } from '@vue/apollo-composable'
import { gql } from 'graphql-tag'
import { Canvas as FabricCanvas, FabricImage } from 'fabric'
import { decodeBase64ToUuid } from '../../../../utils/tool'
import { useLabel   } from '../../../../composables/useLabel'
import type {LabelDetection, CustomRect} from '../../../../composables/useLabel';

const route = useRoute()

const imageIdBase64 = route.params.imageId
const imageId = decodeBase64ToUuid(imageIdBase64 as string)
const datasetId = decodeBase64ToUuid(route.params.id as string)

const canvasEl = ref<HTMLCanvasElement | null>(null)
const fabricCanvas = ref<FabricCanvas | null>(null)
const isDrawingMode = ref(false)

// TODO: Replace with actual user ID from auth system
const userId = '123e4567-e89b-12d3-a456-426614174000'

const IMAGE_QUERY = gql`
  query GetImage($userId: UUID!, $imageId: UUID!) {
    image(userId: $userId, imageId: $imageId) {
      id
      imageName
      imageUrl
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

const { result: imageData } = useQuery(IMAGE_QUERY, {
    userId,
    imageId
})

const { result: labelData, refetch: refetchLabels } = useQuery(LABEL_DETECTIONS_QUERY, {
    datasetId,
    imageId
})

const image = computed(() => imageData.value?.image)
const labels = computed(() => labelData.value?.labelDetections || [])

const {
    startDrawing,
    continueDrawing,
    finishDrawing,
    addExistingLabel,
    handleModification,
    handleDeletion,
    isDrawing
} = useLabel(fabricCanvas, datasetId, imageId, refetchLabels)



const toggleDrawingMode = (state: boolean) => {
    isDrawingMode.value = state
}

const handleMouseDown = (e: MouseEvent) => {
    if (isDrawingMode.value) {
        startDrawing(e)
    }
}

const handleMouseMove = (e: MouseEvent) => {
    if (isDrawingMode.value && isDrawing.value) {
        continueDrawing(e)
    }
}

const handleMouseUp = () => {
    if (isDrawingMode.value && isDrawing.value) {
        finishDrawing()
    }
}

const initCanvas = async () => {
    if (!image.value || !canvasEl.value) return

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
        // Container is wider than image aspect ratio, fit by height
        canvasHeight = containerHeight
        canvasWidth = containerHeight * imageAspectRatio
    } else {
        // Container is taller than image aspect ratio, fit by width
        canvasWidth = containerWidth
        canvasHeight = containerWidth / imageAspectRatio
    }
    
    // Initialize Fabric.js canvas with calculated dimensions
    fabricCanvas.value = new FabricCanvas(canvasEl.value, {
        width: canvasWidth,
        height: canvasHeight,
        uniformScaling: false,
    })


    // Scale image to fit the canvas (now they have the same aspect ratio)
    img.scaleToWidth(canvasWidth)
    
    // Add image to canvas
    fabricCanvas.value.add(img)
    // Centering
    img.set({
        left: fabricCanvas.value.width! / 2,
        top: fabricCanvas.value.height! / 2,
        originX: 'center',
        originY: 'center',
        selectable: false,
        evented: false
    })
    fabricCanvas.value.add(img)

    // Add existing labels
    labels.value.forEach((label: LabelDetection) => {
        addExistingLabel(label)
    })

    // Handle object modifications
    fabricCanvas.value.on('object:modified', async (e) => {
        const rect = e.target as CustomRect;
        if (!rect) return;
        await handleModification(rect)
    })

    fabricCanvas.value.on('object:removed', async (e) => {
        const rect = e.target as CustomRect;
        if (!rect) return;
        await handleDeletion(rect)
    })

    fabricCanvas.value.on('object:moving', (e) => {
        const obj = e.target as CustomRect;
        if (!obj) return;

        // Bounded in canvas
        if (obj.left! < 0) {
            obj.left = 0;
        } else if (obj.left! + obj.width! > fabricCanvas.value!.width!) {
            obj.left = fabricCanvas.value!.width! - obj.width!;
        }

        if (obj.top! < 0) {
            obj.top = 0;
        } else if (obj.top! + obj.height! > fabricCanvas.value!.height!) {
            obj.top = fabricCanvas.value!.height! - obj.height!;
        }
    })

    // Add a test rect
   
    fabricCanvas.value.renderAll()
}

// Function to delete a label from the list
const deleteSelectedLabel = async (label: LabelDetection) => {
    if (!fabricCanvas.value) return

    // Find the corresponding rectangle on canvas
    const objects = fabricCanvas.value.getObjects('rect')
    const rect = objects.find(obj => {
        const customRect = obj as CustomRect
        return customRect.data?.labelId === label.id
    }) as CustomRect | undefined

    if (rect) {
        await handleDeletion(rect)
        fabricCanvas.value.remove(rect)
        fabricCanvas.value.renderAll()
    }
}

// Wrap the original handleKeyDown to add refetch
const handleKeyDown = async (e: KeyboardEvent) => {
    if (!fabricCanvas.value) return

    // Handle backspace or delete key
    if (e.key === 'Backspace' || e.key === 'Delete') {
        const activeObject = fabricCanvas.value.getActiveObject()
        if (activeObject && 'data' in activeObject) {
            const rect = activeObject as CustomRect
            await handleDeletion(rect)
            fabricCanvas.value.remove(rect)
            fabricCanvas.value.renderAll()
        }
    }
}

// Initialize canvas when component is mounted
onMounted(async () => {
    await nextTick()
    if (image.value) {
        initCanvas()
        // Add keyboard event listener with the new handler
        window.addEventListener('keydown', handleKeyDown)
    }

    // Cleanup function
    onUnmounted(() => {
        window.removeEventListener('keydown', handleKeyDown)
        if (fabricCanvas.value) {
            fabricCanvas.value.dispose()
            fabricCanvas.value = null
        }
    })
})
</script>