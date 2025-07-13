import { gql } from 'graphql-tag'
import { useQuery, useMutation } from '@vue/apollo-composable'

export const useLabelQueries = (params: {
  userId: string
  imageId: string
  datasetId: string
}) => {
  // GraphQL Definitions
  const IMAGE_QUERY = gql`
    query GetImage($userId: UUID!, $imageId: UUID!) {
      image(userId: $userId, imageId: $imageId) {
        id
        imageName
        imageUrl
        width
        height
        createdAt
        updatedAt
        caption
        createdBy
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

  const LABEL_SEGMENTATIONS_QUERY = gql`
    query GetLabelSegmentations($datasetId: UUID!, $imageId: UUID!) {
      labelSegmentations(datasetId: $datasetId, imageId: $imageId) {
        id
        classId
        mask
      }
    }
  `

  const LABEL_DETECTIONS_QUERY = gql`
    query GetLabelDetections($datasetId: UUID!, $imageId: UUID!) {
      labelDetections(datasetId: $datasetId, imageId: $imageId) {
        id
        classId
        xCenter
        yCenter
        width
        height
      }
    }
  `

  // Query Hooks
  const { result: imageData } = useQuery(IMAGE_QUERY, {
    userId: params.userId,
    imageId: params.imageId,
  })

  const { result: classesData, refetch: refetchClasses } = useQuery(
    CLASSES_QUERY,
    {
      datasetId: params.datasetId,
    }
  )

  const { result: segmentationData, refetch: refetchSegmentations } = useQuery(
    LABEL_SEGMENTATIONS_QUERY,
    {
      datasetId: params.datasetId,
      imageId: params.imageId,
    }
  )

  const { result: detectionData, refetch: refetchDetections } = useQuery(
    LABEL_DETECTIONS_QUERY,
    {
      datasetId: params.datasetId,
      imageId: params.imageId,
    }
  )

  // Mutation Hooks
  const { mutate: insertClass } = useMutation(INSERT_CLASS_MUTATION)

  // Computed values
  const image = computed(() => imageData.value?.image)
  const classes = computed(() => classesData.value?.classes || [])
  const segmentations = computed(() => segmentationData.value?.labelSegmentations || [])
  const detections = computed(() => detectionData.value?.labelDetections || [])

  return {
    // Data
    image,
    classes,
    segmentations,
    detections,
    // Refetch functions
    refetchClasses,
    refetchSegmentations,
    refetchDetections,
    // Mutations
    insertClass,
  }
}