// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  devtools: { enabled: true },
  nitro: {
    routeRules: {
      '/api/**': { proxy: 'http://proxy:80/api/**' },
    },
  },
})
