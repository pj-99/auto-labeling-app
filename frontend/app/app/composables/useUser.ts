import { useAuth, useUser as clerkUseUser } from '@clerk/vue'
import { useUserStore } from '~/store/user'
import type { UserResource as User } from '@clerk/types'

export function useUser() {
  const { user: clerkUser } = clerkUseUser()
  const { getToken } = useAuth()
  const userStore = useUserStore()

  watch(
    clerkUser,
    async (u) => {
      userStore.setUser(u as User | null)
      if (u) {
        try {
          const t = await getToken.value({ template: 'jwt' })
          userStore.setToken(t as string)
        } catch {
          userStore.setToken('')
        }
      } else {
        userStore.setToken('')
      }
    },
    { immediate: true },
  )

  return userStore
}
