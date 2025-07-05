<template>
    <div class="w-full p-12">
        <!-- Main Content -->
        <div class="mx-auto flex gap-8">
            <!-- Left Sidebar -->
            <div class="w-36 flex flex-col gap-6">
                <UButton icon="i-heroicons-sparkles" color="neutral">
                    Auto Labeling
                </UButton>
                <UButton icon="i-heroicons-pencil-square">
                    {{ isDrawingMode ? 'Exit Drawing Mode' : 'Draw Box' }}
                </UButton>

                <!-- Label Categories -->
                <div class="flex flex-col gap-2">
                    <h2 class="text-lg font-medium mb-2">Label Categories</h2>
                    <div class="space-y-2">
                        <div v-for="i in 7" :key="i" class="flex items-center gap-2">
                            <UCheckbox />
                            <div class="h-0.5 w-16 bg-gray-300"/>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Right Content Area -->
            <div class="flex-1 min-h-[calc(100vh-8rem)]">
                <!-- Image Container -->
                <div
                    class="relative w-full h-[calc(100vh-12rem)] border-2 border-gray-300 rounded-lg bg-gray-50 flex items-center justify-center">
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
import { markRaw, ref, computed, onMounted, onUnmounted, watch, nextTick  } from 'vue';
import { useRoute } from 'vue-router'
import { useQuery } from '@vue/apollo-composable'
import { gql } from 'graphql-tag'
import { Canvas, FabricImage, Rect } from 'fabric'
import { decodeBase64ToUuid } from '../../../../utils/tool'

const route = useRoute()

const imageIdBase64 = route.params.imageId
const imageId = decodeBase64ToUuid(imageIdBase64 as string)


const canvasEl = ref<HTMLCanvasElement | null>(null)
const fabricCanvas = ref<Canvas | null>(null)
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
console.log("imageId", imageId)
const { result: imageData } = useQuery(IMAGE_QUERY, {
    userId,
    imageId
})

const image = computed(() => imageData.value?.image)


const initCanvas = async () => {
    console.log('initCanvas called')
    if (!image.value) {
        console.log('No image data')
        return
    }

    if (!canvasEl.value) {
        console.error('Canvas element not found', {
            canvasEl: canvasEl.value,
            imageData: image.value
        })
        return
    }


    // Initialize Fabric.js canvas
    fabricCanvas.value = new Canvas(canvasEl.value, {
        width: canvasEl.value.parentElement?.clientWidth || 800,
        height: canvasEl.value.parentElement?.clientHeight || 600,
        uniformScaling: false,
    })

    // Load main image
    const img = await FabricImage.fromURL(image.value.imageUrl)

    // // Make image fit to cavnas
    if (img.height > img.width) {
        img.scaleToHeight(fabricCanvas.value.height!)
    } else {
        img.scaleToWidth(fabricCanvas.value.width!)
    }

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

    const rect = new Rect({
        left: 100,
        top: 50,
        fill: 'yellow',
        width: 200,
        height: 100,
        objectCaching: false,
        stroke: 'lightgreen',
        strokeWidth: 4,
        cornerSize: 12,
        cornerStyle: 'circle',
        cornerColor: 'blue',
        transparentCorners: false,
        hasControls: true,
        lockScalingX: false,
        lockScalingY: false,
    });

    fabricCanvas.value.add(markRaw(rect));
    fabricCanvas.value.setActiveObject(rect);
    fabricCanvas.value.renderAll()
}


// Initialize canvas when component is mounted
onMounted(async () => {
    // Wait for next tick to ensure canvas element is mounted
    await nextTick()

    if (image.value) {
        initCanvas()
    }

    // Cleanup function
    onUnmounted(() => {
        if (fabricCanvas.value) {
            fabricCanvas.value.dispose()
            fabricCanvas.value = null
        }
    })
})

// Watch for image changes after mount
watch(() => image.value, () => {
    if (image.value) {
        nextTick(() => {
            initCanvas()
        })
    }
})
</script>