<template>
  <main class="flex flex-col gap-2">
    <h1
      class="text-lg font-bold text-center"
    >
      Messages
    </h1>
    <output
      class="whitespace-pre-line bg-gray-200 dark:bg-gray-800 p-2 rounded-md"
    >
      <p v-if="!messages || messages.length === 0">
        No messages.
      </p>
      <p
        v-for="message in messages"
        class="flex flex-row gap-2 items-center"
      >
        <UButton
          v-if="user?.role === 'administrator'"
          color="red"
          icon="i-heroicons-x-mark-solid"
          :padded="false"
          @click="onDelete(message)"
        />
        <span class="font-bold">{{ message.author }}:</span>
        {{ message.text }}
      </p>
    </output>
    <UForm
      class="flex flex-row gap-2"
      ref="form"
      :schema="schema"
      :state="state"
      :validate-on="['submit']"
      @submit="submit"
    >
      <UFormGroup
        class="w-full"
        name="message"
      >
        <UInput v-model="state.message" />
      </UFormGroup>
      <UButton
        label="Send"
        type="submit"
      />
    </UForm>
  </main>
</template>

<script setup lang="ts">
import { z } from 'zod'
import type { Form, FormSubmitEvent } from '#ui/types'

definePageMeta({
  middleware: 'auth',
})

useSeoMeta({
  title: 'Messages',
})

const { data: user } = await useAuth()
const { data: messages } = await useMessages()

const schema = z.object({
  message: z.string().min(1, 'Must be at least one character'),
})

type Schema = z.output<typeof schema>

const state = reactive({
  message: '',
})

const form = ref<Form<Schema>>()

watch(state, () => form.value!.clear())

watch(
  messages,
  () => {
    const messageList = toValue(messages)

    if (
      messageList.length < 2
      || messageList.at(-2)?.id
    ) {
      return
    }

    messages.value = messageList.filter((message) => message.id)
  },
  { deep: true },
)

async function submit(event: FormSubmitEvent<Schema>) {
  const { data: { message } } = event
  const { first_name, last_name } = user.value!

  messages.value.push({
    id: '',
    date: '',
    author: first_name + (last_name ? ` ${last_name}` : ''),
    text: message,
  })
  state.message = ''

  await sendMessage(message)
}

async function onDelete(message: Message) {
  if (!confirm(
    'Are you sure you want to delete this message?\n'
    + `${message.author}: ${message.text}`
  )) {
    return
  }

  const oldIndex = messages.value.findIndex(
    (oldMessage) => oldMessage.id === message.id
  )
  if (oldIndex !== -1) {
    messages.value.splice(oldIndex, 1)
  }

  await deleteMessage(message.id)
}
</script>
