<script setup lang="ts">
import { getClassColor } from '~/utils/tool'

interface Props {
  imageUrl: string
  alt?: string
  labels?: LabelDetection[] | LabelSegmentation[]
  type?: 'DETECT' | 'SEGMENT'
  lineWidth?: number
}

const props = withDefaults(defineProps<Props>(), {
  alt: 'Labeled image',
  labels: () => [],
  type: 'DETECT',
  lineWidth: 2
})

const canvasRef = ref<HTMLCanvasElement>()
const containerRef = ref<HTMLDivElement>()
const imageLoaded = ref(false)
const imageObj = ref<HTMLImageElement>()

// Computed values for canvas drawing
const scale = ref(1)
const offsetX = ref(0)
const offsetY = ref(0)

// Resize observer
let resizeObserver: ResizeObserver | null = null

const drawCanvas = () => {
  if (!canvasRef.value || !imageObj.value || !imageLoaded.value) return
  
  const canvas = canvasRef.value
  const ctx = canvas.getContext('2d')
  if (!ctx) return

  const containerWidth = canvas.width
  const containerHeight = canvas.height
  const imgWidth = imageObj.value.width
  const imgHeight = imageObj.value.height

  // Clear canvas
  ctx.clearRect(0, 0, containerWidth, containerHeight)

  // Calculate scale and position for object-cover effect
  const containerRatio = containerWidth / containerHeight
  const imageRatio = imgWidth / imgHeight

  let drawWidth, drawHeight, drawX, drawY

  if (imageRatio > containerRatio) {
    // Image is wider, scale by height
    drawHeight = containerHeight
    drawWidth = drawHeight * imageRatio
    drawX = (containerWidth - drawWidth) / 2
    drawY = 0
  } else {
    // Image is taller, scale by width
    drawWidth = containerWidth
    drawHeight = drawWidth / imageRatio
    drawX = 0
    drawY = (containerHeight - drawHeight) / 2
  }

  // Store scale and offset for label positioning
  scale.value = drawWidth / imgWidth
  offsetX.value = drawX
  offsetY.value = drawY

  // Draw image
  ctx.drawImage(imageObj.value, drawX, drawY, drawWidth, drawHeight)

  // Draw labels
  ctx.lineWidth = props.lineWidth

  props.labels.forEach(label => {
    // Convert classId to number and get color
    const classIdNum = parseInt(String(label.classId), 10) || 0
    const color = getClassColor(classIdNum)
    
    if (props.type === 'DETECT' && 'xCenter' in label && 'yCenter' in label) {
      // Detection: Draw bounding boxes
      const x = (label.xCenter - label.width / 2) * imgWidth * scale.value + offsetX.value
      const y = (label.yCenter - label.height / 2) * imgHeight * scale.value + offsetY.value
      const width = label.width * imgWidth * scale.value
      const height = label.height * imgHeight * scale.value

      // Draw filled rectangle with transparency
      ctx.fillStyle = `${color}33` // Add 33 for 20% opacity
      ctx.fillRect(x, y, width, height)
      
      // Draw border
      ctx.strokeStyle = color
      ctx.strokeRect(x, y, width, height)
      
    } else if (props.type === 'SEGMENT' && 'mask' in label) {
      // Segmentation: Draw masks
      // mask is an array of normalized points [x1, y1, x2, y2, ...]
      if (Array.isArray(label.mask) && label.mask.length >= 6) { // Need at least 3 points (6 values) for a polygon
        try {
          const points = [];
          // Convert array of [x1, y1, x2, y2, ...] to array of {x, y} points
          for (let i = 0; i < label.mask.length; i += 2) {
            if (i + 1 < label.mask.length) {
              points.push({
                x: label.mask[i]! * imgWidth * scale.value + offsetX.value,
                y: label.mask[i + 1]! * imgHeight * scale.value + offsetY.value
              });
            }
          }
          
          if (points.length > 2) {
            // Draw filled polygon
            ctx.beginPath();
            ctx.moveTo(points[0]!.x, points[0]!.y);
            points.slice(1).forEach(point => {
              ctx.lineTo(point.x, point.y);
            });
            ctx.closePath();
            
            // Fill with transparent color
            ctx.fillStyle = `${color}33`; // Add 33 for 20% opacity
            ctx.fill();
            
            // Draw outline
            ctx.strokeStyle = color;
            ctx.stroke();
          }
        } catch (error) {
          console.error('Error parsing mask data:', error);
        }
      }
    }
  })
}

const handleResize = () => {
  if (!containerRef.value || !canvasRef.value) return
  
  const rect = containerRef.value.getBoundingClientRect()
  canvasRef.value.width = rect.width
  canvasRef.value.height = rect.height
  
  drawCanvas()
}

const loadImage = () => {
  imageObj.value = new Image()
  imageObj.value.crossOrigin = 'anonymous'
  
  imageObj.value.onload = () => {
    imageLoaded.value = true
    handleResize()
  }
  
  imageObj.value.onerror = () => {
    console.error('Failed to load image:', props.imageUrl)
  }
  
  imageObj.value.src = props.imageUrl
}

onMounted(() => {
  loadImage()
  
  // Set up resize observer
  if (containerRef.value) {
    resizeObserver = new ResizeObserver(handleResize)
    resizeObserver.observe(containerRef.value)
  }
  
  // Initial resize
  handleResize()
})

onUnmounted(() => {
  if (resizeObserver && containerRef.value) {
    resizeObserver.unobserve(containerRef.value)
    resizeObserver.disconnect()
  }
})

// Watch for changes
watch(() => props.imageUrl, () => {
  imageLoaded.value = false
  loadImage()
})

watch(() => props.labels, () => {
  drawCanvas()
}, { deep: true })

watch(() => [props.type], () => {
  drawCanvas()
})
</script>

<template>
  <div ref="containerRef" class="relative w-full h-full overflow-hidden">
    <canvas 
      ref="canvasRef"
      class="absolute inset-0 w-full h-full"
      :aria-label="alt"
    />
    
    <!-- Loading state -->
    <div 
      v-if="!imageLoaded" 
      class="absolute inset-0 flex items-center justify-center bg-gray-100 dark:bg-gray-800"
    >
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-500"/>
    </div>
  </div>
</template>