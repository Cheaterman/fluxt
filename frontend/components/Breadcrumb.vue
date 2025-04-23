<template>
  <UBreadcrumb
    :links="links"
  />
</template>

<script setup lang="ts">
import type { BreadcrumbLink } from '#ui/types'

const route = useRoute()
const routeLinks = {
  '/admin': {
    label: 'Admin',
    icon: 'i-heroicons-home',
  },
  '/admin/users': {
    label: 'Users',
    icon: 'i-heroicons-user-group',
    to: '/admin/users',
  },
  '/admin/users/new': {
    label: 'New user',
    icon: 'i-heroicons-user-plus',
  },
  '/admin/users/edit/': {
    label: 'Edit user',
    icon: 'i-heroicons-pencil-square',
  },
}

const links = computed(() => {
  const _links: BreadcrumbLink[] = []

  for (const [path, link] of Object.entries(routeLinks)) {
    if (
      path !== '/'
      && route.path.includes(path)
      || route.path === path
    ) {
      _links.push(link)
    }
  }

  return _links
})
</script>
