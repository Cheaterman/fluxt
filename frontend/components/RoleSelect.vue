<template>
  <USelect
    v-model="model"
    :options="roleOptions"
  />
</template>

<script setup lang="ts">
const model = defineModel<string>()

const roleOptions = ROLES.map(
  (role) => ({
    label: ROLE_NAMES[role],
    value: role,
  })
)
</script>
