import { useAuth, useUser as clerkUseUser } from '@clerk/vue'
import { useUserStore } from '~/store/user'
import type { UserResource as User } from '@clerk/types'
import gql from 'graphql-tag'

const LOGIN_MUTATION = gql`
  mutation Login($clerkUserId: String!) {
    login(clerkUserId: $clerkUserId) {
      id
      clerkUserId
    }
  }
`

export function useUser() {
  const { user: clerkUser } = clerkUseUser()
  const { getToken } = useAuth()
  const userStore = useUserStore()


  watch(
    clerkUser,
    async (u) => {
      if (u) {
        try {
          // Call Clerk to get the token
          const t = await getToken.value({ template: 'jwt' })
          // Call backend to login (sync user_Id)
          const userId = await login(u.id)
          if (userId) {
            userStore.setToken(t as string) // Set JWT token
            userStore.setUserId(userId) // Set backend user_id
            userStore.setUser(u as User | null) // Set clerk user
            console.log('Backend login successful')
          } else {
            throw new Error('Backend login failed')
          }
        } catch {
          console.log('Error getting token')
        }
      } else {
        userStore.setToken('')
        userStore.setUserId('')
        userStore.setUser(null)
      }
    },
    { immediate: true },
  )

  const { mutate: loginMutation } = useMutation(LOGIN_MUTATION)

  async function login(clerkUserId: string): Promise<string | null> {
    try {
      const result = await loginMutation({ clerkUserId })
      if (result?.data?.login) {
        return result.data.login.id
      }
    } catch (e) {
      console.error('Backend login failed:', e)
    }
    return null
  }

  return userStore
}
