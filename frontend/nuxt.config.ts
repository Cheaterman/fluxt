// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  devtools: { enabled: true },
  // See unity.bar frontend/server/middleware/api.ts
  nitro: {
    routeRules: {
      '/api/**': { proxy: 'http://proxy:80/**' },
    },
  },
  modules: ['@nuxt/ui'],
})
