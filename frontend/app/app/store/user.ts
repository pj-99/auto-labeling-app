import { defineStore } from 'pinia'
import type { UserResource as User } from '@clerk/types'

export const useUserStore = defineStore('user', () => {
  const user = ref<User | null>(null)
  const token = ref<string>('')

  function setUser(u: User | null) {
    user.value = u
  }

  function setToken(t: string) {
    token.value = t
  }

  return {
    user,
    token,
    setUser,
    setToken,
  }
})
