import { useMutation } from '@vue/apollo-composable'
import type { DocumentNode } from 'graphql'

// Type is now properly specified
export const useAutoLabelingMutation = (mutation: DocumentNode, options = {}) => {
  return useMutation(mutation, {
    clientId: 'autoLabeling',
    ...options,
  })
}

export const SAM_MUTATION = gql`
  mutation SAMMutation(
    $imageUrl: String!
    $points: [[[Int!]!]!]!
    $labels: [[Int!]!]!
  ) {
    predictSAM(imageUrl: $imageUrl, points: $points, labels: $labels) {
      boxes {
        xyxy
      }
      masks {
        xy
      }
    }
  }
`

export const PREDICT_GDINO_ON_IMAGE_MUTATION = gql`
  mutation PredictYoloOnImage($imageId: UUID!, $datasetId: UUID!, $userId: UUID!) {
    predictYoloOnImage(imageId: $imageId, datasetId: $datasetId, userId: $userId) {
      ... on PredictJobCreatedSuccess {
        jobId
      }
      ... on PredictJobError {
        message
      }
    }
  }
`

export const PREDICT_GDINO_ON_DATASET_MUTATION = gql`
  mutation PredictYoloOnDataset($datasetId: UUID!, $userId: UUID!) {
    predictYoloOnDataset(datasetId: $datasetId, userId: $userId) {
      ... on PredictJobCreatedSuccess {
        jobId
      }
      ... on PredictJobError {
        message
      }
    }
  }
`