<template>
    <div class="w-full p-12">
        <!-- Main Content -->
        <div class="mx-auto flex gap-8">
            <!-- Left Sidebar -->
            <div class="w-48 shrink-0 flex flex-col gap-6 bg-white rounded-lg shadow-lg border border-gray-200 p-4 h-fit">
                <UButton icon="i-heroicons-sparkles" color="neutral">
                    Auto Labeling
                </UButton>
                <div class="flex flex-col gap-2">
                    <UButton 
                        icon="i-heroicons-pencil-square" 
                        :disabled="!selectedClass"
                        :color="drawingMode === 'segmentation' ? 'primary' : 'neutral'"
                        @click="toggleDrawingMode(drawingMode === 'segmentation' ? 'none' : 'segmentation')"
                    >
                        {{ drawingMode === 'segmentation' ? 'Exit Polygon Mode' : 'Draw Polygon' }}
                        <template #trailing>
                            <span v-if="!selectedClass" class="text-xs text-gray-500">(Select a class first)</span>
                            <span v-else class="text-xs">
                                {{ classItems.find((c: ClassItem) => c.value === selectedClass)?.label }}
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
                <!-- Class List -->
                <div class="flex flex-col gap-2">
                    <h2 class="text-lg font-medium mb-2">Class Selector</h2>
                    <!-- Class Selection -->
                    <USelect
                        v-model="selectedClass"
                        :items="classItems"
                        placeholder="Select a class"
                        icon="i-heroicons-tag"
                        :loading="isAddingClass"
                        class="mb-2"
                    >
                        <template #item="{ item }">
                            <div class="flex items-center gap-2">
                                <div 
                                    class="w-2 h-2 rounded-full" 
                                    :style="{ backgroundColor: getClassColor(item.value) }"
                                />
                                <span>{{ item.label }}</span>
                            </div>
                        </template>
                    </USelect>
                    <!-- Add New Class -->
                    <div class="flex gap-2">
                        <UInput
                            v-model="newClassName"
                            placeholder="New class name"
                            size="sm"
                            class="flex-1"
                            @keyup.enter="createNewClass"
                        />
                        <UButton
                            icon="i-heroicons-plus"
                            color="primary"
                            variant="soft"
                            size="sm"
                            :loading="isAddingClass"
                            :disabled="!newClassName"
                            @click="createNewClass"
                        />
                    </div>
                </div>
                <!-- Label List -->
                <div class="flex flex-col gap-2">
                    <h2 class="text-lg font-medium mb-2">Label List</h2>
                    <div class="space-y-2 max-h-[calc(100vh-36rem)] overflow-y-auto">
                        <div v-if="segmentations.length === 0" class="text-gray-500 text-sm">
                            No labels yet
                        </div>
                        <div
                            v-for="label in segmentations" :key="label.id" 
                            class="flex items-center justify-between p-2 bg-gray-50 rounded-lg hover:bg-gray-100">
                            <div class="flex items-center gap-2">
                                <div 
                                    class="w-2 h-2 rounded-full" 
                                    :style="{ backgroundColor: getClassColor(label.classId) }"
                                />
                                <span class="text-sm">{{ classIdToName.get(label.classId) || `Class ${label.classId}` }}</span>
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
                    class="relative flex-1 border-2 border-gray-300 rounded-lg bg-gray-50 flex items-center justify-center overflow-hidden"
                    @mousedown="handleMouseDown"
                    @mousemove="handleMouseMove"
                    >
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
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue';
import { useRoute } from 'vue-router'
import { useQuery, useMutation } from '@vue/apollo-composable'
import { gql } from 'graphql-tag'
import { Canvas as FabricCanvas, FabricImage } from 'fabric'
import { useLabelSeg } from '../../../../../composables/useLabelSeg'
import type { LabelSegmentation, CustomPolygon } from '../../../../../composables/useLabelSeg'
import type { Ref } from 'vue';

interface Class {
    id: string;
    name: string;
    createdAt: string;
    updatedAt: string;
}

interface ClassItem {
    value: string;
    label: string;
}

const route = useRoute()

const imageIdBase64 = route.params.imageId
const imageId = decodeBase64ToUuid(imageIdBase64 as string)
const datasetId = decodeBase64ToUuid(route.params.id as string)

const canvasEl = ref<HTMLCanvasElement | null>(null)
const fabricCanvas = ref<FabricCanvas | null>(null)
const drawingMode = ref<'none' | 'box' | 'segmentation'>('none')
const isSaving = ref(false)
const selectedClass = ref<string | null>(null)
const newClassName = ref('')
const isAddingClass = ref(false)

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

const LABEL_SEGMENTATIONS_QUERY = gql`
  query GetLabelSegmentations($datasetId: UUID!, $imageId: UUID!) {
    labelSegmentations(datasetId: $datasetId, imageId: $imageId) {
      id
      classId
      mask
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

const { result: imageData } = useQuery(IMAGE_QUERY, {
    userId,
    imageId
})

const { result: segmentationData, refetch: refetchSegmentations } = useQuery(LABEL_SEGMENTATIONS_QUERY, {
    datasetId,
    imageId
})

const { result: classesData, refetch: refetchClasses } = useQuery(CLASSES_QUERY, {
    datasetId
})

const { mutate: insertClass } = useMutation(INSERT_CLASS_MUTATION)

const image = computed(() => imageData.value?.image)
const segmentations = computed(() => segmentationData.value?.labelSegmentations || [])
const classes = computed(() => classesData.value?.classes || [] as Class[])

// Format classes for USelect
const classItems = computed(() => classes.value.map((cls: Class) => ({
    label: cls.name,
    value: cls.id,
})))

// Create a map of class ID to name
const classIdToName = computed(() => {
    const map = new Map<string, string>()
    classes.value.forEach((cls: Class) => {
        map.set(cls.id, cls.name)
    })
    return map
})



const wrappedRefetchSegmentations = async () => {
    await refetchSegmentations()
}


const {
    startDrawing: startSegDrawing,
    continueDrawing: continueSegDrawing,
    finishDrawing: _finishSegDrawing, // Prefix with _ to indicate it's intentionally unused
    addExistingLabel: addExistingSegmentation,
    handleModification: handleSegModification,
    handleDeletion: handleSegDeletion,
    handleKeyDown: handleSegKeyDown,
    isDrawing: isSegDrawing,
} = useLabelSeg(fabricCanvas as Ref<FabricCanvas | null>, datasetId, imageId, wrappedRefetchSegmentations, selectedClass, getClassColor)

// Update drawing mode toggle
const toggleDrawingMode = (mode: 'none' | 'box' | 'segmentation') => {
    drawingMode.value = mode
    if (!fabricCanvas.value) return

    // Disable selection when in drawing mode
    fabricCanvas.value.selection = mode === 'none'
}

// Combined mouse event handlers
const handleMouseDown = (e: MouseEvent) => {
    if (drawingMode.value === 'segmentation') {
        startSegDrawing(e)
    }
}

const handleMouseMove = (e: MouseEvent) => {
    if (drawingMode.value === 'segmentation' && isSegDrawing.value) {
        continueSegDrawing(e)
    }
}


// Combined keyboard event handler
const handleKeyDown = async (e: KeyboardEvent) => {
    await handleSegKeyDown(e)       
}


// Initialize canvas with both types of labels
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
    fabricCanvas.value.add(markRaw(img))
    // Centering
    img.set({
        left: fabricCanvas.value.width! / 2,
        top: fabricCanvas.value.height! / 2,
        originX: 'center',
        originY: 'center',
        selectable: false,
        evented: false
    })


    console.log("labels segmentations", segmentations.value)
    // Add existing segmentation labels
    segmentations.value.forEach((label: LabelSegmentation) => {
        console.log("segementation Label mask", label.mask)
        addExistingSegmentation(label)
    })

    fabricCanvas.value.on('object:moving', (e) => {
        console.log("object:moving", e)
        const obj = e.target as CustomPolygon;
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

    // Handle object modifications
    fabricCanvas.value.on('object:modified', async (e) => {
        const obj = e.target
        if (!obj || !('data' in obj)) return

        console.log("object:modified seg", obj)
        await handleSegModification(obj as CustomPolygon)
    })

    fabricCanvas.value.renderAll()
}

// Function to delete a label from the list
const deleteSelectedLabel = async (label: LabelDetection) => {
    if (!fabricCanvas.value) return

    // Find the corresponding rectangle on canvas
    const objects = fabricCanvas.value.getObjects('polygon')
    const target = objects.find(obj => {
        const customPolygon = obj as CustomPolygon
        return customPolygon.data?.labelId === label.id
    }) as CustomPolygon | undefined

    if (target) {
        await handleSegDeletion(target)
    }
}


// TODO: this function can be rewrite
// Use variable to keep track of the current modification
const saveCurrentModifications = async () => {
    if (!fabricCanvas.value) return
    
    isSaving.value = true
    try {
        // Get all rectangle objects from canvas
        const objects = fabricCanvas.value.getObjects('polygon')
        // Update each rectangle
        for (const obj of objects) {
            const polygon = obj as CustomPolygon
            if (polygon) {
                await handleSegModification(polygon)
            }
        }
    } finally {
        isSaving.value = false
    }
}

const createNewClass = async () => {
    if (!newClassName.value) return
    
    isAddingClass.value = true
    try {
        await insertClass({
            datasetId,
            name: newClassName.value
        })
        newClassName.value = ''
        await refetchClasses()
    } catch (error) {
        console.error('Failed to create class:', error)
    } finally {
        isAddingClass.value = false
    }
}

// Initialize canvas when component is mounted and watch for image changes
onMounted(async () => {
    await nextTick()
    if (image.value) {
        initCanvas()
        // Add keyboard event listener with the new handler
        window.addEventListener('keydown', handleKeyDown)
    }
})

// // Watch for image changes
// watch(() => image.value?.imageUrl, async (newUrl, oldUrl) => {
//     if (newUrl && newUrl !== oldUrl) {
//         await nextTick()
//         initCanvas()
//     }
// }, { immediate: true })


// Cleanup function
onUnmounted(() => {
    window.removeEventListener('keydown', handleKeyDown)
    if (fabricCanvas.value) {
        fabricCanvas.value.dispose()
        fabricCanvas.value = null
    }
})



// Watch for image changes
watch(() => image.value?.imageUrl, async (newUrl, oldUrl) => {
    if (newUrl && newUrl !== oldUrl) {
        // dispose the canvas
        if (fabricCanvas.value) {
            fabricCanvas.value.dispose()
            fabricCanvas.value = null
        }

        initCanvas()
    }
}, { immediate: true })



</script>