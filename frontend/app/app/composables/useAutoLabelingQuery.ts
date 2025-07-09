// composables/useAutoLabelingQuery.ts
import { useMutation } from '@vue/apollo-composable'

// TODO: Fix the any type for mutation
export const useAutoLabelingMutation = (mutation: any, options = {}) => {
  return useMutation(mutation, {
    clientId: 'autoLabeling',
    ...options,
  })
}

export const SAMMutation = gql`
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
