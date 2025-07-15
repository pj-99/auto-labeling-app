import { useUserStore } from '~/store/user'

export default defineNuxtPlugin((nuxtApp) => {
    nuxtApp.hook('apollo:auth', ({ token }) => {
        const userStore = useUserStore()
        const authToken = userStore.token
        if (authToken) {
            token.value = authToken
        }
    })
}) 