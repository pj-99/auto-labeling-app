// composables/useAutoLabelingQuery.ts
import { useMutation } from '@vue/apollo-composable'



export const useAutoLabelingMutation = (mutation: any, options = {}) => {


    return useMutation(mutation, {
        clientId: "autoLabeling",
        ...options
    })
}

export const SAMMutation = gql`
  mutation SAMMutation($imageUrl: String!, $points: [[Int!]!]!, $labels: [Int!]!) {
    predict(imageUrl: $imageUrl, points: $points, labels: $labels) {
      boxes {
        xyxy
      }
      masks {
        xy
      }
    }
  }
`