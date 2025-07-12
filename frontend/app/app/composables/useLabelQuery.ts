// composables/useLabelQuery.ts
import { gql } from '@apollo/client/core'
import { useApolloClient } from '@vue/apollo-composable'

// Queries
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

const LABEL_SEGMENTATIONS_QUERY = gql`
  query GetLabelSegmentations($datasetId: UUID!, $imageId: UUID!) {
    labelSegmentations(datasetId: $datasetId, imageId: $imageId) {
      id
      classId
      mask
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

// Types
export interface LabelDetection {
  id: string
  classId: string
  xCenter: number
  yCenter: number
  width: number
  height: number
}

export interface LabelSegmentation {
  id: string
  classId: string
  mask: string // or whatever format your mask is in
}

export interface DatasetClass {
  id: string
  name: string
  createdAt: string
  updatedAt: string
}

export function useLabelQuery() {
  const { resolveClient } = useApolloClient()
  const apollo = resolveClient()

  // Fetch detection labels
  const fetchLabelDetections = async (datasetId: string, imageId: string): Promise<LabelDetection[]> => {
    const { data } = await apollo.query({
      query: LABEL_DETECTIONS_QUERY,
      variables: { datasetId, imageId },
      fetchPolicy: 'network-only',
    })
    return data.labelDetections
  }

  // Fetch segmentation labels
  const fetchLabelSegmentations = async (datasetId: string, imageId: string): Promise<LabelSegmentation[]> => {
    const { data } = await apollo.query({
      query: LABEL_SEGMENTATIONS_QUERY,
      variables: { datasetId, imageId },
      fetchPolicy: 'network-only',
    })
    return data.labelSegmentations
  }

  // Fetch dataset classes
  const fetchClasses = async (datasetId: string): Promise<DatasetClass[]> => {
    const { data } = await apollo.query({
      query: CLASSES_QUERY,
      variables: { datasetId },
      fetchPolicy: 'network-only',
    })
    return data.classes
  }

  // Fetch labels based on training type
  const fetchLabels = async (datasetId: string, imageId: string, trainingType: 'DETECT' | 'SEGMENT') => {
    if (trainingType === 'DETECT') {
      return fetchLabelDetections(datasetId, imageId)
    } else {
      return fetchLabelSegmentations(datasetId, imageId)
    }
  }

  // Cache for classes to avoid repeated queries
  const classesCache = ref<Map<string, DatasetClass[]>>(new Map())

  // Fetch classes with caching
  const fetchClassesWithCache = async (datasetId: string): Promise<DatasetClass[]> => {
    if (classesCache.value.has(datasetId)) {
      return classesCache.value.get(datasetId)!
    }
    
    const classes = await fetchClasses(datasetId)
    classesCache.value.set(datasetId, classes)
    return classes
  }

  // Get class name by ID
  const getClassName = async (datasetId: string, classId: string): Promise<string | undefined> => {
    const classes = await fetchClassesWithCache(datasetId)
    return classes.find(c => c.id === classId)?.name
  }

  // Fetch labels with class names
  const fetchLabelsWithClassNames = async (
    datasetId: string, 
    imageId: string, 
    trainingType: 'DETECT' | 'SEGMENT'
  ) => {
    const [labels, classes] = await Promise.all([
      fetchLabels(datasetId, imageId, trainingType),
      fetchClassesWithCache(datasetId)
    ])

    // Create a map for quick class lookup
    const classMap = new Map(classes.map(c => [c.id, c.name]))

    // Add className to each label
    return labels.map(label => ({
      ...label,
      className: classMap.get(label.classId) || 'Unknown'
    }))
  }

  return {
    fetchLabelDetections,
    fetchLabelSegmentations,
    fetchClasses,
    fetchLabels,
    fetchClassesWithCache,
    getClassName,
    fetchLabelsWithClassNames,
  }
}