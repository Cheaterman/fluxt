declare module '#app' {
  interface NuxtApp {
    $api: typeof $fetch
  }
}

declare module 'vue' {
  interface ComponentCustomProperties {
    $api: typeof $fetch
  }
}

export default defineNuxtPlugin(() => {
  const config = useRuntimeConfig()
  const headers = useRequestHeaders(['cookie'])

  const $api = $fetch.create({
    baseURL: config.app.baseURL + '/api',
    headers,
  })
  return { provide: { api: $api } }
})
