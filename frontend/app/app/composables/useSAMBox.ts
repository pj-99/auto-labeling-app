import type { Canvas as FabricCanvas } from 'fabric'
import { Circle } from 'fabric'
import type { CustomRect } from './useLabel'
import type { ToastProps } from '@nuxt/ui'

export type SAMMode = 'add' | 'remove'

export interface SAMBboxSession {
  rect: CustomRect | null
  points: Array<[number, number]>
  labels: number[]  // 1 for positive, 0 for negative
}

export interface SAMPredictResult {
  data?: {
    predictSAM: {
      boxes: Array<{
        xyxy: number[]
      }>
    }
  }
}

export interface SAMPredictRequest {
  imageUrl: string
  points: Array<Array<[number, number]>>
  labels: Array<number[]>
}

export interface BoxDimensions {
  classId: number;
  xCenter: number;
  yCenter: number;
  width: number;
  height: number;
}

export const useSAMBbox = (
  fabricCanvas: Ref<FabricCanvas | null>,
  selectedClass: Ref<number | undefined>,
  selectedModel: Ref<string>,
  imageWidth: Ref<number | undefined>,
  addExistingBox: (label: BoxDimensions) => CustomRect | null,
  handleBoxModification: (rect: CustomRect) => Promise<string | null>,
  updateBoxesSelectability: () => void,
  wrappedRefetchLabels: () => Promise<void>,
  predictSam: (params: SAMPredictRequest) => Promise<SAMPredictResult | null>,
  xyxyToXCenterYCenter: (xyxy: number[], width: number, height: number) => BoxDimensions,
  toast: { add: (params: ToastProps) => void }
) => {
  // State
  const samMode = ref<SAMMode>('add')
  const isAutoLabelLoading = ref(false)

  const activeSAMSession = ref<SAMBboxSession>({
    rect: null,
    points: [],
    labels: []
  })

  // Computed
  const isInSAMEditing = computed(() =>
    selectedModel.value === 'SAM' && activeSAMSession.value.rect !== null
  )

  // SAM Points Rendering for Bbox
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

  // SAM Bbox Prediction
  const pointToBoxBySAM = async (
    pointX: number,
    pointY: number,
    imageUrl: string,
    imageWidth: number,
    imageHeight: number,
    isPositive: boolean = true
  ) => {
    if (!selectedClass.value) {
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

    if (!result || !result.data?.predictSAM.boxes || result.data.predictSAM.boxes.length === 0) {
      toast.add({
        title: 'No bounding box detected',
        description: 'Try clicking on a different part of the object',
        color: 'warning',
      })
      return
    }

    // Get the first box (best prediction)
    const box = result.data.predictSAM.boxes[0]
    const { xCenter, yCenter, width, height } = xyxyToXCenterYCenter(
      box!.xyxy,
      imageWidth,
      imageHeight
    )

    // Remove previous rect if exists
    if (activeSAMSession.value.rect) {
      fabricCanvas.value!.remove(activeSAMSession.value.rect as CustomRect)
    }

    // Create new rect with dashed line
    const rect = addExistingBox({
      classId: selectedClass.value,
      xCenter,
      yCenter,
      width,
      height,
    })

    if (rect) {
      rect.set({
        strokeDashArray: [5, 5],
        selectable: false,
        evented: false
      })

      activeSAMSession.value.rect = rect
    }

    renderSAMPoints()
    fabricCanvas.value!.renderAll()
  }

  // SAM Session Management
  const confirmSAMBbox = async () => {
    if (!activeSAMSession.value.rect) return

    const rect = activeSAMSession.value.rect

    // Clear points first
    clearSAMPoints()

    // Update rect state
    rect.set({
      strokeDashArray: [],
      selectable: true,
      evented: true
    })

    // Save modification
    const newLabelId = await handleBoxModification(rect as CustomRect)

    if (newLabelId && !rect.data?.labelId) {
      rect.data!.labelId = newLabelId
    }

    // Clean up
    fabricCanvas.value!.discardActiveObject()
    updateBoxesSelectability()
    fabricCanvas.value!.renderAll()

    // Reset session
    activeSAMSession.value = {
      rect: null,
      points: [],
      labels: []
    }

    await wrappedRefetchLabels()
  }

  const cancelSAMBbox = () => {
    if (activeSAMSession.value.rect) {
      fabricCanvas.value!.remove(activeSAMSession.value.rect as CustomRect)
    }

    clearSAMPoints()

    activeSAMSession.value = {
      rect: null,
      points: [],
      labels: []
    }

    fabricCanvas.value!.renderAll()
  }

  // Handle SAM click
  const handleSAMClick = async (
    e: MouseEvent,
    imageUrl: string,
    imageWidth: number,
    imageHeight: number,
    getMousePoint: (e: MouseEvent, canvas: FabricCanvas, imageWidth: number) => { x: number; y: number }
  ) => {
    if (selectedModel.value !== 'SAM' || !imageWidth) return

    try {
      isAutoLabelLoading.value = true
      const { x, y } = getMousePoint(e, fabricCanvas.value!, imageWidth)
      await pointToBoxBySAM(x, y, imageUrl, imageWidth, imageHeight, samMode.value === 'add')
      updateBoxesSelectability()
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
        await confirmSAMBbox()
        return true
      } else if (e.key === 'Escape' || e.key === 'Backspace' || e.key === 'Delete') {
        e.preventDefault()
        cancelSAMBbox()
        return true
      }
    }
    return false
  }

  // Clean up when switching modes
  const cleanupSAM = () => {
    if (isInSAMEditing.value) {
      cancelSAMBbox()
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
    pointToBoxBySAM,
    confirmSAMBbox,
    cancelSAMBbox,
    handleSAMClick,
    handleSAMKeyboard,
    cleanupSAM
  }
}