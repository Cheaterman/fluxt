<template>
  <UModal
    v-model="model"
    prevent-close
  >
    <UCard>
      <template #header>
        <h2
          class="text-lg font-bold"
        >
          {{ title }}
        </h2>
      </template>

      <p>
        {{ content }}
      </p>

      <template #footer>
        <div class="flex flex-row justify-center gap-2">
          <UButton
            v-bind="button"
          />
        </div>
      </template>
    </UCard>
  </UModal>
</template>

<script setup lang="ts">
import type { Button } from '#ui/types'

const model = defineModel<boolean>()
const {
  title,
  content,
  button = { label: 'Ok', to: '/' },
} = defineProps<{
  title: string,
  content: string,
  button?: Button,
}>()
</script>
