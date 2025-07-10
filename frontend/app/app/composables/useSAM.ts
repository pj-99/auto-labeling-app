import type { Canvas as FabricCanvas } from 'fabric'
import { Circle } from 'fabric'
import type { CustomPolygon } from './useLabelSeg'
import type { ToastProps } from '@nuxt/ui'

export type SAMMode = 'add' | 'remove'

export interface SAMSession {
  polygon: CustomPolygon | null
  points: Array<[number, number]>
  labels: number[]  // 1 for positive, 0 for negative
}

export interface SAMPredictResult {
  data?: {
    predictSAM: {
      masks: Array<{
        xy: Array<[number, number]>
      }>
    }
  }
}

export interface SAMPredictParams {
  imageUrl: string
  points: Array<Array<[number, number]>>
  labels: Array<number[]>
}

export const useSAM = (
  fabricCanvas: Ref<FabricCanvas | null>,
  selectedClass: Ref<number | undefined>,
  selectedModel: Ref<string | null>,
  imageWidth: Ref<number | undefined>,
  addPolygon: (points: { x: number; y: number }[], classId: number) => CustomPolygon | null,
  handleSegModification: (polygon: CustomPolygon) => Promise<string | null>,
  updatePolygonsSelectability: () => void,
  wrappedRefetchSegmentations: () => Promise<void>,
  predictSam: (params: SAMPredictParams) => Promise<SAMPredictResult | null>,
  toast: { add: (params: ToastProps) => void }
) => {
  // State
  const samMode = ref<SAMMode>('add')
  const isAutoLabelLoading = ref(false)
  
  const activeSAMSession = ref<SAMSession>({
    polygon: null,
    points: [],
    labels: []
  })

  // Computed
  const isInSAMEditing = computed(() => 
    selectedModel.value === 'SAM' && activeSAMSession.value.polygon !== null
  )

  // SAM Points Rendering
  const renderSAMPoints = () => {
    if (!fabricCanvas.value || !imageWidth.value) return
    
    // Remove existing points
    const existingPoints = fabricCanvas.value.getObjects().filter(
      obj => 'data' in obj && obj.data && typeof obj.data === 'object' && 'type' in obj.data && obj.data.type === 'sam-point'
    )
    existingPoints.forEach(point => fabricCanvas.value!.remove(point))
    
    // Render new points
    activeSAMSession.value.points.forEach((point, index) => {
      const isPositive = activeSAMSession.value.labels[index] === 1
      const scaleFactor = fabricCanvas.value!.width! / imageWidth.value!
      
      const outerCircle = new Circle({
        radius: 8,
        fill: 'white',
        stroke: 'white',
        strokeWidth: 2,
        left: point[0] * scaleFactor,
        top: point[1] * scaleFactor,
        originX: 'center',
        originY: 'center',
        selectable: false,
        evented: false,
        data: { type: 'sam-point', index }
      })
      
      const innerCircle = new Circle({
        radius: 5,
        fill: isPositive ? '#10b981' : '#ef4444',
        stroke: isPositive ? '#059669' : '#dc2626',
        strokeWidth: 1,
        left: point[0] * scaleFactor,
        top: point[1] * scaleFactor,
        originX: 'center',
        originY: 'center',
        selectable: false,
        evented: false,
        data: { type: 'sam-point', index }
      })
      
      fabricCanvas.value!.add(outerCircle, innerCircle)
    })
    
    fabricCanvas.value!.renderAll()
  }

  const clearSAMPoints = () => {
    if (!fabricCanvas.value) return
    
    const points = fabricCanvas.value.getObjects().filter(
      obj => 'data' in obj && obj.data && typeof obj.data === 'object' && 'type' in obj.data && obj.data.type === 'sam-point'
    )
    points.forEach(point => fabricCanvas.value!.remove(point))
    fabricCanvas.value!.renderAll()
  }

  // SAM Prediction
  const pointToSegBySAM = async (
    pointX: number, 
    pointY: number, 
    imageUrl: string,
    isPositive: boolean = true
  ) => {
    if (!imageWidth.value || !selectedClass.value) {
      toast.add({
        title: 'Please select a class first',
        color: 'error',
      })
      return
    }

    // Update session points
    if (isInSAMEditing.value) {
      activeSAMSession.value.points.push([pointX, pointY])
      activeSAMSession.value.labels.push(isPositive ? 1 : 0)
    } else {
      activeSAMSession.value.points = [[pointX, pointY]]
      activeSAMSession.value.labels = [isPositive ? 1 : 0]
    }

    // Predict
    const result = await predictSam({
      imageUrl: imageUrl,
      points: [activeSAMSession.value.points],
      labels: [activeSAMSession.value.labels],
    })

    if (!result || !result.data?.predictSAM.masks.length) return

    const mask = result.data.predictSAM.masks[0]
    const points = mask!.xy.map((point: [number, number]) => ({
      x: point[0],
      y: point[1],
    }))

    const scaleFactor = fabricCanvas.value!.width! / imageWidth.value!
    const normalizedPoints = points.map((point: { x: number; y: number }) => ({
      x: point.x * scaleFactor,
      y: point.y * scaleFactor,
    }))

    // Remove previous polygon if exists
    if (activeSAMSession.value.polygon) {
      fabricCanvas.value!.remove(activeSAMSession.value.polygon as CustomPolygon)
    }

    // Add new polygon
    const newPolygon = addPolygon(normalizedPoints, selectedClass.value!)
    
    if (newPolygon) {
      newPolygon.set({
        strokeDashArray: [5, 5],
        selectable: false,
        evented: false
      })
      
      activeSAMSession.value.polygon = newPolygon
    }

    renderSAMPoints()
    fabricCanvas.value!.renderAll()
  }

  // SAM Session Management
  const confirmSAMSegmentation = async () => {
    if (!activeSAMSession.value.polygon) return
    
    const polygon = activeSAMSession.value.polygon as CustomPolygon
    
    // Clear points first
    clearSAMPoints()
    
    // Update polygon state
    polygon.set({
      strokeDashArray: [],
      selectable: true,
      evented: true
    })
    
    // Prepare data
    if (!polygon.data) {
      polygon.data = {
        labelId: '', 
        classId: selectedClass.value!
      }
    }
    
    // Remove labelId if empty to avoid UUID error
    if (!polygon.data.labelId || polygon.data.labelId === '') {
      delete (polygon.data as { labelId?: string, classId: number }).labelId
    }
    
    // Save modification
    const newLabelId = await handleSegModification(polygon)
    
    if (newLabelId) {
      polygon.data.labelId = newLabelId
    }
    
    // Clean up
    fabricCanvas.value!.discardActiveObject()
    updatePolygonsSelectability()
    fabricCanvas.value!.renderAll()
    
    // Reset session
    activeSAMSession.value = {
      polygon: null,
      points: [],
      labels: []
    }
    
    await wrappedRefetchSegmentations()
  }

  const cancelSAMSegmentation = () => {
    if (activeSAMSession.value.polygon) {
      fabricCanvas.value!.remove(activeSAMSession.value.polygon as CustomPolygon)
    }
    
    clearSAMPoints()
    
    activeSAMSession.value = {
      polygon: null,
      points: [],
      labels: []
    }
    
    fabricCanvas.value!.renderAll()
  }

  // Handle SAM click
  const handleSAMClick = async (
    e: MouseEvent, 
    imageUrl: string,
    getMousePoint: (e: MouseEvent, canvas: FabricCanvas, imageWidth: number) => { x: number; y: number }
  ) => {
    if (selectedModel.value !== 'SAM' || !imageWidth.value) return
    
    try {
      isAutoLabelLoading.value = true
      const { x, y } = getMousePoint(e, fabricCanvas.value!, imageWidth.value)
      await pointToSegBySAM(x, y, imageUrl, samMode.value === 'add')
      updatePolygonsSelectability()
    } catch (error) {
      console.error('Failed to auto-label:', error)
      toast.add({
        title: 'Auto-labeling failed',
        description: 'Please try again',
        color: 'error'
      })
    } finally {
      isAutoLabelLoading.value = false
    }
  }

  // Handle keyboard shortcuts for SAM
  const handleSAMKeyboard = async (e: KeyboardEvent): Promise<boolean> => {
    if (selectedModel.value === 'SAM' && isInSAMEditing.value) {
      if (e.key === 'Enter') {
        e.preventDefault()
        await confirmSAMSegmentation()
        return true
      } else if (e.key === 'Escape' || e.key === 'Backspace' || e.key === 'Delete') {
        e.preventDefault()
        cancelSAMSegmentation()
        return true
      }
    }
    return false
  }

  // Clean up when switching modes
  const cleanupSAM = () => {
    if (isInSAMEditing.value) {
      cancelSAMSegmentation()
    }
  }

  return {
    // State
    samMode,
    isAutoLabelLoading,
    activeSAMSession,
    isInSAMEditing,
    
    // Methods
    renderSAMPoints,
    clearSAMPoints,
    pointToSegBySAM,
    confirmSAMSegmentation,
    cancelSAMSegmentation,
    handleSAMClick,
    handleSAMKeyboard,
    cleanupSAM
  }
}