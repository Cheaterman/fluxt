<template>
  <UHorizontalNavigation
    class="border-b border-gray-200"
    :links="links"
  />
</template>

<script setup lang="ts">
import type { HorizontalNavigationLink } from '#ui/types'

const { data: user, refresh } = await useAuth()

const links: HorizontalNavigationLink[][] = [
  [
    {
      label: 'Messages',
      icon: 'i-heroicons-chat-bubble-bottom-center-text',
      to: '/',
    },
  ],
  [
    {
      label: 'Log out',
      icon: 'i-heroicons-arrow-right-on-rectangle',
      click: async () => {
        await logout()
        await refresh()
        return navigateTo('/login')
      },
    },
  ],
]

if (toValue(user)?.role === 'administrator') {
  links[0].push({
    label: 'Users',
    icon: 'i-heroicons-user-group',
    to: '/admin/users',
  })
}
</script>
