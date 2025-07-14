import { defineStore } from 'pinia'
import type { UserResource as User } from '@clerk/types'
import { computed } from 'vue'


export const useUserStore = defineStore('user', () => {
  const clerkUser = ref<User | null>(null)
  const token = ref<string>('')
  const userId = ref<string>('') // The userId in backend

  function setUser(u: User | null) {
    clerkUser.value = u
  }

  function setToken(t: string) {
    token.value = t
  }

  function setUserId(id: string) {
    userId.value = id
  }

  const isAuthenticated = computed(() => !!token.value)

  return {
    clerkUser,
    token,
    userId,
    isAuthenticated,
    setUser,
    setToken,
    setUserId
  }
})
