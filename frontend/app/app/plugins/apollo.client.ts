import { DefaultApolloClient } from '@vue/apollo-composable'
import type { ApolloClient } from '@apollo/client/core'
import { defineNuxtPlugin } from '#app'

export default defineNuxtPlugin((nuxtApp) => {
    const defaultClient = (nuxtApp.$apollo as any).defaultClient as ApolloClient<unknown>
    nuxtApp.vueApp.provide(DefaultApolloClient, defaultClient)
})