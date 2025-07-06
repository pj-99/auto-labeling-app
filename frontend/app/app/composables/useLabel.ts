import type { Ref } from 'vue';
import { ref, markRaw } from 'vue'
import type { Canvas as FabricCanvas } from 'fabric';
import { Rect } from 'fabric'
import { gql } from 'graphql-tag'
import { useMutation } from '@vue/apollo-composable'
export interface LabelDetection {
    id?: string
    classId: string
    xCenter: number
    yCenter: number
    width: number
    height: number
}

interface UpsertLabelDetectionSuccess {
    __typename: 'UpsertLabelDetectionSuccess'
    labels: Array<{
        id: string
        classId: string
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
        labelId: string
        classId: string
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
    imageId: string,
    onLabelUpdate?: () => Promise<void>,
    selectedClassId?: Ref<string | null>,
    getClassColor?: (classId: string) => string
) => {
    const currentRect = ref<CustomRect | null>(null)
    const isDrawing = ref(false)
    const startPoint = ref<{ x: number; y: number } | null>(null)

    const { mutate: upsertLabels } = useMutation(UPSERT_LABELS_MUTATION)
    const { mutate: deleteLabel } = useMutation(DELETE_LABEL_MUTATION)

    const createRect = (options: Partial<CustomRect>) => {
        const classId = options.data?.classId || selectedClassId?.value
        const color = classId && getClassColor ? getClassColor(classId) : 'blue'

        return new Rect({
            fill: 'transparent',
            stroke: color,
            strokeWidth: 2,
            cornerSize: 8,
            cornerStyle: 'circle',
            cornerColor: color,
            transparentCorners: false,
            hasControls: true,
            ...options
        }) as CustomRect
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
        })

        currentRect.value = rect
        // Without markRaw, scaling object will not work
        canvas.add(markRaw(rect))
        canvas.renderAll()
    }

    const continueDrawing = (e: MouseEvent) => {
        if (!isDrawing.value || !startPoint.value || !currentRect.value || !fabricCanvas.value) return

        const canvas = fabricCanvas.value
        const pointer = canvas.getPointer(e)
        const width = pointer.x - startPoint.value.x
        const height = pointer.y - startPoint.value.y

        currentRect.value.set({
            width: Math.abs(width),
            height: Math.abs(height),
            left: width > 0 ? startPoint.value.x : pointer.x,
            top: height > 0 ? startPoint.value.y : pointer.y
        })

        canvas.renderAll()
    }

    const finishDrawing = async () => {
        if (!isDrawing.value || !currentRect.value || !fabricCanvas.value || !selectedClassId?.value) return

        isDrawing.value = false
        const canvas = fabricCanvas.value
        const rect = currentRect.value

        // Convert to normalized coordinates
        const canvasWidth = canvas.width!
        const canvasHeight = canvas.height!

        const labelDetection = {
            classId: selectedClassId.value, // No need to parse as int anymore
            xCenter: (rect.left! + rect.width! / 2) / canvasWidth,
            yCenter: (rect.top! + rect.height! / 2) / canvasHeight,
            width: rect.width! / canvasWidth,
            height: rect.height! / canvasHeight
        }

        try {
            const { data } = await upsertLabels({
                datasetId,
                imageId,
                labelDetections: [labelDetection]
            }) as { data: UpsertLabelResult }

            if (data?.upsertLabelDetections.__typename === 'UpsertLabelDetectionSuccess') {
                const labels = data.upsertLabelDetections.labels
                if (labels && labels.length > 0) {
                    const newLabel = labels[0]
                    if (newLabel) {
                        rect.data = {
                            labelId: newLabel.id,
                            classId: newLabel.classId
                        }
                        await onLabelUpdate?.()
                    }
                }
            }
        } catch (error) {
            console.error('Failed to create label:', error)
        }

        currentRect.value = null
        startPoint.value = null
        canvas.renderAll()

        isDrawing.value = false
    }

    const addExistingLabel = (label: LabelDetection) => {
        if (!fabricCanvas.value) return
        const labelWidth = label.width * fabricCanvas.value.width!
        const labelHeight = label.height * fabricCanvas.value.height!

        const rect = createRect({
            left: (label.xCenter * fabricCanvas.value.width!) - labelWidth / 2,
            top: (label.yCenter * fabricCanvas.value.height!) - labelHeight / 2,
            width: labelWidth,
            height: labelHeight,
            data: {
                labelId: label.id!,
                classId: label.classId
            },
        })

        fabricCanvas.value.add(markRaw(rect))
        fabricCanvas.value.renderAll()
    }

    const handleModification = async (rect: CustomRect) => {
        if (!fabricCanvas.value) return

        const canvasWidth = fabricCanvas.value.width!
        const canvasHeight = fabricCanvas.value.height!
        const scaleX = rect.scaleX!
        const scaleY = rect.scaleY!

        const labelDetection = {
            id: rect.data?.labelId,
            classId: rect.data?.classId || "1",
            xCenter: (rect.left! + rect.width! / 2) / canvasWidth,
            yCenter: (rect.top! + rect.height! / 2) / canvasHeight,
            width: (rect.width! * scaleX) / canvasWidth,
            height: (rect.height! * scaleY) / canvasHeight
        }

        try {
            await upsertLabels({
                datasetId,
                imageId,
                labelDetections: [labelDetection]
            })
            await onLabelUpdate?.()
        } catch (error) {
            console.error('Failed to update label:', error)
        }
    }

    const handleDeletion = async (rect: CustomRect) => {
        if (rect?.data?.labelId) {
            try {
                await deleteLabel({
                    labelId: rect.data.labelId
                })
                await onLabelUpdate?.()
            } catch (error) {
                console.error('Failed to delete label:', error)
            }
        }
    }

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

    return {
        startDrawing,
        continueDrawing,
        finishDrawing,
        addExistingLabel,
        handleModification,
        handleDeletion,
        handleKeyDown,
        isDrawing,
        currentRect
    }
} 