<template>
  <div class="flex flex-row gap-8 items-start">
    <input
      ref="input"
      type="file"
      class="hidden"
      :accept="accept"
      :disabled="uploading"
      @change="onChange($event)"
    />
    <div class="flex flex-col">
      <UButton
        icon="i-heroicons-photo"
        color="black"
        :loading="uploading"
        @click="input?.click()"
      >
        Browse
      </UButton>

      <p class="text-xs text-gray-600">
        Accepted formats: {{ acceptedText }}
      </p>

      <p class="text-xs text-red-800 bold">
        {{ error }}
      </p>
    </div>

    <template v-if="file">
      <img
        v-if="!file.endsWith('.mp4')"
        class="h-20"
        :src="useFile(file)"
      />
      <video
        v-else
        controls
        width="142"
      >
        <source
          :src="useFile(file)"
          type="video/mp4"
        />
      </video>
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'

const file = defineModel<string>()
const input = ref<HTMLInputElement>()
const uploading = ref(false)
const error = ref('')

const props = withDefaults(defineProps<{
  accept?: string
}>(), {
  accept: 'image/png, image/jpeg',
})

const MIME_TO_EXTS: Record<string, readonly string[]> = {
  'image/jpeg': ['.jpg', '.jpeg'],
  'image/png': ['.png'],
  'video/mp4': ['.mp4'],
  'video/webm': ['.webm'],
  'application/pdf': ['pdf'],
  [
    'application/vnd.openxmlformats-'
    + 'officedocument.spreadsheetml.sheet'
  ]: ['xlsx'],
}

const WILDCARD_TO_EXTS: Record<string, readonly string[]> = {
  'image/*': ['.png', '.jpg', '.jpeg'],
  'video/*': ['.mp4', '.webm'],
  'application/*': ['.pdf', '.xlsx'],
}

function parseAcceptToExtensions(accept: string): string[] {
  const tokens = (
    (accept ?? '')
    .split(',')
    .map(s => s.trim().toLowerCase())
    .filter(Boolean)
  )

  const extensions = new Set<string>()

  for (const tok of tokens) {
    if (tok.startsWith('.')) {
      extensions.add(tok)
      continue
    }

    const wildcard = WILDCARD_TO_EXTS[tok]
    if (wildcard) {
      for (const ext of wildcard) {
        extensions.add(ext)
      }
      continue
    }

    const known = MIME_TO_EXTS[tok]
    if (known) {
      for (const ext of known) {
        extensions.add(ext)
      }
      continue
    }

    extensions.add(tok)
  }

  return [...extensions]
}

const acceptedText = computed(() => {
  const extensions = parseAcceptToExtensions(props.accept)

  const preferredOrder = [
    '.png',
    '.jpg',
    '.jpeg',
    '.mp4',
    '.webm',
    '.pdf',
    '.xlsx',
  ]

  extensions.sort((a, b) => {
    const indexA = preferredOrder.indexOf(a)
    const indexB = preferredOrder.indexOf(b)

    if (indexA === -1 && indexB === -1) {
      return a.localeCompare(b)
    }
    if (indexA === -1) {
      return 1
    }
    if (indexB === -1) {
      return -1
    }

    return indexA - indexB
  })

  return extensions.join(', ')
})

async function onChange(event: Event) {
  const target = event.target as HTMLInputElement

  if (!target.files?.length) {
    return
  }

  const _file = target.files[0]
  uploading.value = true

  try {
    const response = await uploadFile(_file)
    file.value = response.filename
  }
  catch (_) {
    error.value = 'Invalid file.'
    setTimeout(() => (error.value = ''), 5000)
  }

  uploading.value = false
}
</script>
