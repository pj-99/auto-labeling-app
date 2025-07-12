import type { Ref } from 'vue'
import { ref, markRaw } from 'vue'
import type { Canvas as FabricCanvas, FabricObject } from 'fabric'
import { Rect } from 'fabric'
import { gql } from 'graphql-tag'
import { useMutation } from '@vue/apollo-composable'
export interface LabelDetection {
  id?: string
  classId: number | 0
  xCenter: number
  yCenter: number
  width: number
  height: number
}

interface UpsertLabelDetectionSuccess {
  __typename: 'UpsertLabelDetectionSuccess'
  labels: Array<{
    id: string
    classId: number
    xCenter: number
    yCenter: number
    width: number
    height: number
  }>
}

interface UpsertLabelError {
  __typename: 'UpsertLabelError'
  message: string
  code: string
}

type UpsertLabelResult = {
  upsertLabelDetections: UpsertLabelDetectionSuccess | UpsertLabelError
}

export interface CustomRect extends Rect {
  data?: {
    labelId?: string
    classId?: number
  }
}

const UPSERT_LABELS_MUTATION = gql`
  mutation UpsertLabelDetections(
    $datasetId: UUID!
    $imageId: UUID!
    $labelDetections: [LabelDetectionInputGraphql!]!
  ) {
    upsertLabelDetections(
      datasetId: $datasetId
      imageId: $imageId
      labelDetections: $labelDetections
    ) {
      ... on UpsertLabelDetectionSuccess {
        labels {
          id
          classId
          xCenter
          yCenter
          width
          height
        }
      }
      ... on UpsertLabelError {
        message
        code
      }
    }
  }
`

const DELETE_LABEL_MUTATION = gql`
  mutation DeleteLabelDetection($labelId: UUID!) {
    deleteLabelDetections(labelId: $labelId) {
      ... on DeleteLabelSuccess {
        success
      }
      ... on DeleteLabelError {
        message
        code
      }
    }
  }
`

export const useLabel = (
  fabricCanvas: Ref<FabricCanvas | null>,
  datasetId: string,
  refetch: () => Promise<void>,
  imageId: string,
  selectedClassId?: Ref<number | undefined>,
) => {
  const currentRect = ref<CustomRect | null>(null)
  const isDrawing = ref(false)
  const startPoint = ref<{ x: number; y: number } | null>(null)

  const { mutate: upsertLabels } = useMutation(UPSERT_LABELS_MUTATION)
  const { mutate: deleteLabel } = useMutation(DELETE_LABEL_MUTATION)

const createRect = (options: Partial<CustomRect>) => {
  const classId = options.data?.classId ?? selectedClassId?.value
const color = (classId !== undefined && classId !== null && getClassColor) ? getClassColor(classId) : 'blue'

  const rect = new Rect({
    fill: 'transparent',
    stroke: color,
    strokeWidth: 3,
    cornerSize: 8,
    cornerStyle: 'circle',
    cornerColor: 'teal',
    cornerStrokeColor: 'white',
    transparentCorners: false,
    hasControls: true,
    rotateWithControls: false,
    rotate: false,
    lockRotation: true,
    hasBorders: false,
    selectable: true,
    evented: true,
    ...options,
  }) as CustomRect

  rect.setControlsVisibility({
    mt: true, // middle top
    mb: true, // middle bottom
    ml: true, // middle left
    mr: true, // middle right
    tl: true, // top left
    tr: true, // top right
    bl: true, // bottom left
    br: true, // bottom right
    mtr: false,
  })

  return rect
}

  const startDrawing = (e: MouseEvent) => {
    if (!fabricCanvas.value) return

    const canvas = fabricCanvas.value
    const pointer = canvas.getPointer(e)
    isDrawing.value = true
    startPoint.value = { x: pointer.x, y: pointer.y }

    const rect = createRect({
      left: pointer.x,
      top: pointer.y,
      width: 0,
      height: 0,
      data: {
        classId: selectedClassId?.value ?? 0
      }
    })
    console.log('Starting drawing with rect:', rect)

    currentRect.value = rect
    // Without markRaw, scaling object will not work
    canvas.add(markRaw(rect))
    canvas.renderAll()
  }

  const continueDrawing = (e: MouseEvent) => {
    if (
      !isDrawing.value ||
      !startPoint.value ||
      !currentRect.value ||
      !fabricCanvas.value
    )
      return
    const canvas = fabricCanvas.value
    const pointer = canvas.getPointer(e)
    const width = pointer.x - startPoint.value.x
    const height = pointer.y - startPoint.value.y

    currentRect.value.set({
      width: Math.abs(width),
      height: Math.abs(height),
      left: width > 0 ? startPoint.value.x : pointer.x,
      top: height > 0 ? startPoint.value.y : pointer.y,
    })

    canvas.renderAll()
  }

const finishDrawing = async () => {
 if (
   !isDrawing.value ||
   !currentRect.value ||
   !fabricCanvas.value
 )
   return

 isDrawing.value = false
 const canvas = fabricCanvas.value
 const rect = currentRect.value

 // Save rect properties
 const rectProps = {
   left: rect.left!,
   top: rect.top!,
   width: rect.width!,
   height: rect.height!,
 }

 // Convert to normalized coordinates
 const canvasWidth = canvas.width!
 const canvasHeight = canvas.height!
 
 const labelDetection = {
   classId: selectedClassId?.value ?? 0,
   xCenter: (rectProps.left + rectProps.width / 2) / canvasWidth,
   yCenter: (rectProps.top + rectProps.height / 2) / canvasHeight,
   width: rectProps.width / canvasWidth,
   height: rectProps.height / canvasHeight,
 }

 let newLabelId = ''
 
 try {
   const { data } = (await upsertLabels({
     datasetId,
     imageId,
     labelDetections: [labelDetection],
   })) as { data: UpsertLabelResult }

   if (
     data?.upsertLabelDetections.__typename === 'UpsertLabelDetectionSuccess'
   ) {
     const labels = data.upsertLabelDetections.labels
     if (labels && labels.length > 0) {
       const newLabel = labels[0]
       if (newLabel) {
         newLabelId = newLabel.id
       }
     }
   }
 } catch (error) {
   console.error('Failed to create label:', error)
 }

 // Remove the temporary rect
 canvas.remove(rect as unknown as FabricObject)

 // Create a new rect using createRect
 const newRect = createRect({
   ...rectProps,
   data: {
     labelId: newLabelId,
     classId: selectedClassId!.value ?? 0,
   },
 })
 
 canvas.add(markRaw(newRect))
 
 currentRect.value = null
 startPoint.value = null
 canvas.renderAll()

 isDrawing.value = false
 await refetch()
}

  const addExistingLabel = (label: LabelDetection): CustomRect | null => {
    if (!fabricCanvas.value) return null
    const labelWidth = label.width * fabricCanvas.value.width!
    const labelHeight = label.height * fabricCanvas.value.height!

    const rect = createRect({
      left: label.xCenter * fabricCanvas.value.width! - labelWidth / 2,
      top: label.yCenter * fabricCanvas.value.height! - labelHeight / 2,
      width: labelWidth,
      height: labelHeight,
      data: {
        labelId: label.id!,
        classId: label.classId,
      },
    })

    fabricCanvas.value.add(markRaw(rect))
    fabricCanvas.value.renderAll()
    return rect
  }

  const handleModification = async (
    rect: CustomRect
  ): Promise<string | null> => {
    if (!fabricCanvas.value) return null

    const canvasWidth = fabricCanvas.value.width!
    const canvasHeight = fabricCanvas.value.height!
    const scaleX = rect.scaleX!
    const scaleY = rect.scaleY!

    const labelDetection = {
      id: rect.data?.labelId,
      classId: rect.data?.classId || '1',
      xCenter: (rect.left! + rect.width! / 2) / canvasWidth,
      yCenter: (rect.top! + rect.height! / 2) / canvasHeight,
      width: (rect.width! * scaleX) / canvasWidth,
      height: (rect.height! * scaleY) / canvasHeight,
    }

    try {
      const result = await upsertLabels({
        datasetId,
        imageId,
        labelDetections: [{ ...labelDetection }],
      })
      if (!result || !result.data) return null
      if (
        result.data?.upsertLabelDetections.__typename ===
        'UpsertLabelDetectionSuccess'
      ) {
        if (result.data.upsertLabelDetections.labels.length > 0) {
          return result.data.upsertLabelDetections.labels[0].id
        }
      }
      await refetch()
    } catch (error) {
      console.error('Failed to update label:', error)
    }
    return null
  }

  const handleDeletion = async (rect: CustomRect) => {
    if (rect?.data?.labelId) {
      try {
        await deleteLabel({
          labelId: rect.data.labelId,
        })
        await refetch()
      } catch (error) {
        console.error('Failed to delete label:', error)
      }
    }
  }

  return {
    startDrawing,
    continueDrawing,
    finishDrawing,
    addExistingLabel,
    handleModification,
    handleDeletion,
    isDrawing,
    currentRect,
  }
}
