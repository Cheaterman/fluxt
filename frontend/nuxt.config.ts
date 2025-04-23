// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  icon: {
    localApiEndpoint: '/_nuxt_icon_api',
  },
  modules: ['@nuxt/ui'],
  vite: {
    server: {
      allowedHosts: ['frontend'],
    },
  },
  compatibilityDate: '2025-04-01',
})
