import { useAutoLabelingMutation, PREDICT_GDINO_ON_IMAGE_MUTATION } from '~/composables/useAutoLabelingQuery'

interface GDINOOptions {
    imageId: string
    datasetId: string
    userId: string
    onComplete?: () => Promise<void>
}

export const useGDINO = () => {
    const isGDINOLoading = ref(false)
    const { mutate: predictGDINOOnImage } = useAutoLabelingMutation(PREDICT_GDINO_ON_IMAGE_MUTATION)
    const toast = useToast()

    const runGDINO = async (options: GDINOOptions) => {
        const { imageId, datasetId, userId, onComplete } = options
        
        isGDINOLoading.value = true
        
        try {
            const result = await predictGDINOOnImage({
                imageId,
                datasetId,
                userId
            })
            
            // Process the returned result - need to confirm the correct response structure
            const data = result?.data?.predictGDINOOnImage || result?.data?.predictYoloOnImage
            const jobId = data?.jobId
            const errorMessage = data?.message
            
            if (jobId) {
                toast.add({
                    title: 'YOLO inference started',
                    description: 'Processing, please wait...',
                    icon: 'i-heroicons-arrow-path',
                    color: 'success'
                })
                
                // TODO: Can be changed to WebSocket or polling to check status in the future
                // Currently using setTimeout as a temporary solution
                setTimeout(async () => {
                    // Callback after completion (usually refetch)
                    if (onComplete) {
                        await onComplete()
                    }
                    
                    toast.add({
                        title: 'YOLO inference complete',
                        description: 'Annotations updated',
                        icon: 'i-heroicons-check-circle',
                        color: 'success'
                    })
                    
                    isGDINOLoading.value = false
                }, 10000) // Check after 10 seconds
                
            } else if (errorMessage) {
                toast.add({
                    title: 'Inference failed',
                    description: errorMessage,
                    color: 'error'
                })
                isGDINOLoading.value = false
            } else {
                // Case with no jobId and no error message
                toast.add({
                    title: 'Inference request abnormal',
                    description: 'Please try again later',
                    color: 'warning'
                })
                isGDINOLoading.value = false
            }
        } catch (error) {
            console.error('GDINO prediction failed:', error)
            toast.add({
                title: 'Inference request failed',
                description: 'Please check network connection',
                color: 'error'
            })
            isGDINOLoading.value = false
        }
    }

    // Cancel ongoing inference (if needed)
    const cancelGDINO = () => {
        // TODO: Implement cancellation logic
        isGDINOLoading.value = false
    }

    return {
        isGDINOLoading,
        runGDINO,
        cancelGDINO
    }
}