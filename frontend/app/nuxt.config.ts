// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  devtools: { enabled: true },

  modules: [
    '@nuxt/ui',
    '@nuxt/eslint',
    '@nuxt/icon',
    '@nuxt/image',
    '@nuxtjs/apollo',
    '@pinia/nuxt',
    '@clerk/nuxt',
  ],

  css: ['~/assets/css/main.css'],

  future: {
    compatibilityVersion: 4,
  },

  compatibilityDate: '2024-11-27',

  apollo: {
    clients: {
      default: {
        httpEndpoint: process.env.NUXT_APOLLO_DEFAULT_ENDPOINT || 'http://localhost:8000/graphql',
      },
      autoLabeling: {
        httpEndpoint: process.env.NUXT_APOLLO_AUTO_LABELING_ENDPOINT || 'http://localhost:8080/graphql',
      },
    },
  },

  runtimeConfig: {
    public: {
      // For image uploading
      apiBase: process.env.NUXT_PUBLIC_API_BASE || 'http://localhost:8000',
    },
  },
})