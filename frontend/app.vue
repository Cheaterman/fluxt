<template>
  <div>
    <UContainer class="space-y-2">
      <template v-if="user">
        <Navigation />
        <Breadcrumb />
      </template>
      <NuxtPage />
    </UContainer>

    <UNotifications />
  </div>
</template>

<script setup lang="ts">
useHead({
  titleTemplate: (title) =>
    title
    ? `${title} - %siteName`
    : '%siteName'
  ,
  templateParams: { siteName: 'Fluxt demo' },
})

const { data: user } = await useAuth()

const toast = useToast()
const error = useError()

watch(error, () => {
  const _error = toValue(error)

  if (_error && _error.statusCode === 403) {
    toast.add({
      title: 'Error',
      icon: 'i-heroicons-x-circle-16-solid',
      color: 'red',
      description: _error.message,
    })
    clearError()
  }
})
</script>
