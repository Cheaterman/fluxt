<template>
  <main class="flex flex-col gap-2">
    <h1
      class="text-lg font-bold w-full text-center"
    >
      Set your password
    </h1>
    <UForm
      class="space-y-2"
      ref="form"
      :schema="schema"
      :state="state"
      @submit="submit"
    >
      <UFormGroup
        name="password"
        label="Password"
        required
      >
        <UInput
          v-model="state.password"
          type="password"
        />
      </UFormGroup>
      <UFormGroup name="errors" />
      <div
        class="flex flex-row gap-2 mt-2 justify-center"
      >
        <UButton
          label="Submit"
          type="submit"
        />
      </div>
    </UForm>
    <MessageModal
      v-model="isMessageOpen"
      v-bind="message"
    />
  </main>
</template>

<script setup lang="ts">
import { z } from 'zod'
import type { Form, FormSubmitEvent } from '#ui/types'
import { FetchError } from 'ofetch'

useSeoMeta({
  title: 'Set your password',
})

const schema = z.object({
  password: z.string().min(4),
})

type Schema = z.output<typeof schema>

const form = ref<Form<Schema>>()

const state = reactive({
  password: undefined,
})

const isMessageOpen = ref(false)
const message = ref<{
  title: string,
  content: string,
}>({
  title: '',
  content: '',
})

const token = useRoute().params.token as string

try {
  await getPasswordState(token)
}
catch (error) {
  if (error instanceof FetchError) {
    switch (error.status) {
      case 409:
        message.value = {
          title: 'Password already set',
          content: 'Your password is already set. You can now sign in.',
        }
      break

      case 404:
        message.value = {
          title: 'Invalid link',
          content: 'The link you followed seems invalid. Try to sign in instead.',
        }
      break

      default:
        message.value = {
          title: 'Unknown error',
          content: 'An unknown error has occured. Please try again later.',
        }
    }
    isMessageOpen.value = true
  }
}

async function submit(event: FormSubmitEvent<Schema>) {
  const { data: { password } } = event

  try {
    await setPassword(token, password)
  }
  catch (error) {
    if (error instanceof FetchError) {
      return
    }
  }

  message.value = {
    title: 'Password successfully set',
    content: 'Your password was successfully set. You can now sign in.',
  }
  isMessageOpen.value = true
}
</script>
