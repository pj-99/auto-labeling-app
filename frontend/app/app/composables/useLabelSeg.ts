// TODO: support adding vertex
import type { Ref } from 'vue';
import { ref } from 'vue'
import { controlsUtils, Point, Polygon } from 'fabric';
import type { Canvas as FabricCanvas, FabricObject, XY } from 'fabric';
import { gql } from 'graphql-tag'
import { useMutation } from '@vue/apollo-composable'

export interface LabelSegmentation {
    id?: string
    classId: number
    mask: number[] // Normalized points [x1, y1, x2, y2, ...]
}

interface UpsertLabelSegmentationSuccess {
    __typename: 'UpsertLabelSegmentationSuccess'
    labels: Array<{
        id: string
        classId: number
        mask: number[]
    }>
}

interface UpsertLabelError {
    __typename: 'UpsertLabelError'
    message: string
    code: string
}

type UpsertLabelResult = {
    upsertLabelSegmentations: UpsertLabelSegmentationSuccess | UpsertLabelError
}

export interface CustomPolygon extends Polygon {
    editing: boolean
    data?: {
        labelId: string
        classId: number
    }
}

const UPSERT_LABELS_MUTATION = gql`
  mutation UpsertLabelSegmentations(
    $datasetId: UUID!
    $imageId: UUID!
    $labelSegmentations: [LabelSegmentationInputGraphql!]!
  ) {
    upsertLabelSegmentations(
      datasetId: $datasetId
      imageId: $imageId
      labelSegmentations: $labelSegmentations
    ) {
      ... on UpsertLabelSegmentationSuccess {
        labels {
          id
          classId
          mask
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
  mutation DeleteLabelSegmentation($labelId: UUID!) {
    deleteLabelSegmentations(labelId: $labelId) {
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

export const useLabelSeg = (
    fabricCanvas: Ref<FabricCanvas | null>,
    datasetId: string,
    refetch: () => Promise<void>,
    imageId: string,
    selectedClassId?: Ref<number | null>,
) => {
    const currentPolygon = ref<CustomPolygon | null>(null)
    const isDrawing = ref(false)
    const points = ref<{ x: number; y: number }[]>([])

    const { mutate: upsertLabels } = useMutation(UPSERT_LABELS_MUTATION)
    const { mutate: deleteLabel } = useMutation(DELETE_LABEL_MUTATION)

    const createPolygon = (options: { points: { x: number; y: number }[]; data?: { labelId: string; classId: number } }) => {
        const classId = options.data?.classId || selectedClassId?.value
        const color = classId && getClassColor ? getClassColor(classId) : 'blue'

        const polygon = new Polygon(options.points, {
            fill: `${color}33`, // Add transparency
            stroke: color,
            strokeWidth: 2,
            cornerSize: 8,
            cornerStyle: 'circle',
            cornerColor: color,
            transparentCorners: false,
            hasControls: true,
            objectCaching: false,
        }) as CustomPolygon;

        polygon.editing = false;
        polygon.controls = controlsUtils.createObjectDefaultControls();

        // Enable editing when double click
        polygon.on('mousedblclick', () => {
            polygon.editing = !polygon.editing
            if (polygon.editing) {
                polygon.cornerStyle = 'circle';
                polygon.cornerColor = 'rgba(0,0,255,0.5)';
                polygon.hasBorders = false;
                polygon.controls = controlsUtils.createPolyControls(polygon);
            } else {
                polygon.cornerColor = 'blue';
                polygon.cornerStyle = 'rect';
                polygon.hasBorders = true;
                polygon.controls = controlsUtils.createObjectDefaultControls();
            }
            polygon.setCoords();
            fabricCanvas.value?.requestRenderAll();
        })

        if (options.data) {
            polygon.data = options.data
        }

        return polygon
    }

    const startDrawing = (e: MouseEvent) => {
        if (!fabricCanvas.value || !selectedClassId?.value) return

        const canvas = fabricCanvas.value
        const pointer = canvas.getPointer(e)

        if (!isDrawing.value) {
            // Start new polygon
            isDrawing.value = true
            points.value = [{ x: pointer.x, y: pointer.y }]
            // Create initial polygon with single point
            const newPolygon = createPolygon({
                points: points.value
            })

            currentPolygon.value = newPolygon
            canvas.add(markRaw(newPolygon))
        } else {
            // Add point to existing polygon
            points.value.push({ x: pointer.x, y: pointer.y })

            if (currentPolygon.value) {
                currentPolygon.value.set('points', points.value)
            }
        }

        canvas.renderAll()
    }

    const continueDrawing = (e: MouseEvent) => {
        if (!isDrawing.value || !currentPolygon.value || !fabricCanvas.value) return

        const pointer = fabricCanvas.value.getScenePoint(e)

        if (points.value.length > 0) {
            currentPolygon.value?.set('points', [...points.value, { x: pointer.x, y: pointer.y }])
            currentPolygon.value?.setCoords()

            fabricCanvas.value.renderAll()
        }
    }

    const finishDrawing = async () => {
        if (!isDrawing.value || !currentPolygon.value || !fabricCanvas.value || !selectedClassId?.value) return

        const canvas = fabricCanvas.value
        const polygon = currentPolygon.value

        // Convert points to normalized coordinates
        const canvasWidth = canvas.width ?? 1
        const canvasHeight = canvas.height ?? 1
        const normalizedPoints: number[] = []

        points.value.forEach(point => {
            normalizedPoints.push(point.x / canvasWidth)  // Normalize x
            normalizedPoints.push(point.y / canvasHeight) // Normalize y
        })

        const labelSegmentation = {
            classId: selectedClassId.value,
            mask: normalizedPoints
        }

        try {
            const { data } = await upsertLabels({
                datasetId,
                imageId,
                labelSegmentations: [labelSegmentation]
            }) as { data: UpsertLabelResult }

            if (data?.upsertLabelSegmentations.__typename === 'UpsertLabelSegmentationSuccess') {
                const labels = data.upsertLabelSegmentations.labels
                if (labels && labels.length > 0) {
                    const newLabel = labels[0]
                    if (newLabel) {
                        polygon.data = {
                            labelId: newLabel.id,
                            classId: newLabel.classId
                        }
                    }
                }
            }
        } catch (error) {
            console.error('Failed to create segmentation label:', error)
        }


        // Somehow the finied polygon cannot be selected
        // So workaround by adding a identical polygon
        const newPolygon = createPolygon({
            points: points.value,
            data: {
                classId: polygon.data?.classId || selectedClassId.value,
                labelId: polygon.data?.labelId || ""
            },
        })
        canvas.add(markRaw(newPolygon))
        canvas.remove(currentPolygon.value as unknown as FabricObject)
        canvas.renderAll()

        // Reset drawing state
        currentPolygon.value.selectable = true
        currentPolygon.value = null
        points.value = []

        isDrawing.value = false

        await refetch()
    }

    const addPolygon = (points: { x: number; y: number }[], classId: number) => {
        const polygon = createPolygon({
            points: points,
            data: {
                labelId: null,
                classId: classId
            },
        })
        fabricCanvas.value?.add(markRaw(polygon))
        return polygon
    }

    const addExistingLabel = async (label: LabelSegmentation): Promise<CustomPolygon | null> => {
        if (!fabricCanvas.value) return null
        const canvas = fabricCanvas.value

        // Convert normalized points back to canvas coordinates
        const canvasPoints: { x: number; y: number }[] = []

        for (let i = 0; i < label.mask.length; i += 2) {
            canvasPoints.push({
                x: label.mask[i] * (canvas.width ?? 1),
                y: label.mask[i + 1] * (canvas.height ?? 1)
            })
        }

        const polygon = createPolygon({
            points: canvasPoints,
            data: {
                labelId: label.id!,
                classId: label.classId
            },
        })

        canvas.add(markRaw(polygon))
        canvas.renderAll()

        return polygon
    }

    const handleModification = async (polygon: CustomPolygon): Promise<string | null> => {
        if (!fabricCanvas.value) return null

        const canvas = fabricCanvas.value
        const canvasWidth = canvas.width ?? 1
        const canvasHeight = canvas.height ?? 1

        // Get normalized points after modification
        const normalizedPoints: number[] = []
        const points = getPoints(polygon)
        points.forEach(point => {
            normalizedPoints.push(point.x / canvasWidth)
            normalizedPoints.push(point.y / canvasHeight)
        })

        const labelSegmentation = {
            id: polygon.data?.labelId,
            classId: polygon.data?.classId || selectedClassId?.value || "1",
            mask: normalizedPoints
        }

        try {
            const result = await upsertLabels({
                datasetId,
                imageId,
                labelSegmentations: [labelSegmentation]
            })
            if (!result) {
                console.error('Failed to update segmentation label:', result)
                return null
            }
            if (result.data?.upsertLabelSegmentations.__typename === 'UpsertLabelSegmentationSuccess') {
                const labels = result.data.upsertLabelSegmentations.labels
                if (labels && labels.length > 0) {
                    return labels[0].id
                }
            }
            return null
        } catch (error) {
            console.error('Failed to update segmentation label:', error)
            return null
        }
    }

    const handleDeletion = async (polygon: CustomPolygon) => {
        if (polygon?.data?.labelId) {
            try {
                await deleteLabel({
                    labelId: polygon.data.labelId
                })
            } catch (error) {
                console.error('Failed to delete segmentation label:', error)
            }
        }
        fabricCanvas.value?.remove(polygon)
        await refetch()
    }

    const handleKeyDown = async (e: KeyboardEvent) => {
        console.log("useLabelSeg handleKeyDown", e)
        if (!fabricCanvas.value) return

        if (e.key === 'Escape' && isDrawing.value) {
            // Cancel current polygon drawing
            isDrawing.value = false
            points.value = []
            if (currentPolygon.value) {
                fabricCanvas.value.remove(currentPolygon.value as unknown as FabricObject)
                currentPolygon.value = null
                fabricCanvas.value.renderAll()
            }
            fabricCanvas.value.renderAll()
        } else if (e.key === 'Enter' && isDrawing.value) {
            // Complete current polygon
            await finishDrawing()
        } else if ((e.key === 'Backspace' || e.key === 'Delete') && !isDrawing.value) {
            // Delete selected polygon
            const activeObject = fabricCanvas.value.getActiveObject()
            if (activeObject && 'data' in activeObject) {
                const polygon = activeObject as CustomPolygon
                await handleDeletion(polygon)
                fabricCanvas.value.remove(polygon)
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
        currentPolygon,
        addPolygon
    }
}

// Get absolute points of a polygon
function getPoints(polygon: Polygon): XY[] {
    const matrix = polygon.calcTransformMatrix();
    return polygon
        .get('points')
        .map((p: Point) =>
            new Point(p.x - polygon.pathOffset.x, p.y - polygon.pathOffset.y),
        )
        .map((p: Point) => p.transform(matrix));
}