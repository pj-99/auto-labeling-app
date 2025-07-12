// composables/useImageUpload.ts
import { useMutation } from '@vue/apollo-composable'
import { gql } from 'graphql-tag'

const INSERT_IMAGE_MUTATION = gql`
  mutation InsertImageToDataset(
    $userId: UUID!
    $datasetId: UUID!
    $gcsFileName: String!
    $imageName: String!
    $imageType: String!
    $width: Int!
    $height: Int!
  ) {
    insertImageToDataset(
      userId: $userId
      datasetId: $datasetId
      gcsFileName: $gcsFileName
      imageName: $imageName
      imageType: $imageType
      width: $width
      height: $height
    ) {
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

export const useImageUpload = () => {
  const toast = useToast()
  const uploading = ref(false)
  const { mutate: insertImageMutation } = useMutation(INSERT_IMAGE_MUTATION)
  
  const getSignedUrl = async (contentType: string) => {
    const {
      public: { apiBase },
    } = useRuntimeConfig()

    try {
      const response = await fetch(`${apiBase}/generate-signed-url`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ content_type: contentType }),
      })

      if (!response.ok) {
        throw new Error('Failed to get signed URL')
      }

      return await response.json()
    } catch (error) {
      console.error('Error getting signed URL:', error)
      throw error
    }
  }

  const uploadFileToGCS = async (file: File, signedUrl: string) => {
    try {
      const response = await fetch(signedUrl, {
        method: 'PUT',
        headers: {
          'Content-Type': file.type,
        },
        body: file,
      })

      if (!response.ok) {
        throw new Error('Failed to upload file to storage')
      }
    } catch (error) {
      console.error('Error uploading to GCS:', error)
      throw error
    }
  }

  const uploadImages = async (
    files: FileList | File[],
    datasetId: string,
    userId: string,
    onSuccess?: () => void
  ) => {
    const fileArray = Array.from(files)
    uploading.value = true
    let successCount = 0
    const failedFiles: string[] = []

    try {
      for (const file of fileArray) {
        try {
          // Step 1: Get signed URL for the file
          const { url: signedUrl, filename } = await getSignedUrl(file.type)
          
          // Step 2: Upload the file to GCS using the signed URL
          await uploadFileToGCS(file, signedUrl)
          
          // Step 3: Get image dimensions
          const { width, height } = await getImageDimensions(file)
          
          // Step 4: Insert image record via GraphQL mutation
          await insertImageMutation({
            userId,
            datasetId,
            gcsFileName: filename,
            imageName: file.name,
            imageType: file.type,
            width: width,
            height: height,
          })
          
          successCount++
        } catch (error) {
          console.error(`Failed to upload ${file.name}:`, error)
          failedFiles.push(file.name)
        }
      }

      // Show appropriate notifications
      if (successCount > 0) {
        toast.add({
          title: `Successfully uploaded ${successCount} images`,
          color: 'success',
          duration: 5000,
          icon: 'i-heroicons-check-circle',
        })
      }
      
      if (failedFiles.length > 0) {
        toast.add({
          title: `${failedFiles.length} images failed to upload`,
          description: `Failed files: ${failedFiles.join(', ')}`,
          color: 'error',
          duration: 5000,
          icon: 'i-heroicons-exclamation-triangle',
        })
      }

      if (onSuccess) {
        onSuccess()
      }
    } catch (error) {
      console.error('Upload error:', error)
      toast.add({
        title: 'Upload failed',
        description: error instanceof Error ? error.message : 'An unknown error occurred',
        color: 'error',
        duration: 5000,
        icon: 'i-heroicons-exclamation-triangle',
      })
    } finally {
      uploading.value = false
    }
  }

  return {
    uploading: readonly(uploading),
    uploadImages
  }
}