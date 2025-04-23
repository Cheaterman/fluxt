<template>
  <main class="flex flex-col gap-2">
    <h1
      class="text-lg font-bold w-full text-center"
    >
      Please input your e-mail to reset your password
    </h1>
    <UForm
      class="space-y-2"
      ref="form"
      :schema="schema"
      :state="state"
      @submit="submit"
    >
      <UFormGroup
        name="email"
        label="E-mail"
        required
      >
        <UInput
          v-model="state.email"
        />
      </UFormGroup>
      <div
        class="flex flex-row gap-2 mt-2 justify-center"
      >
        <UButton
          label="Cancel"
          color="gray"
          variant="outline"
          @click="$router.back()"
        />
        <UButton
          label="Reset"
          type="submit"
        />
      </div>
      <UFormGroup name="errors" />
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

useSeoMeta({
  title: 'Reset your password',
})

const schema = z.object({
  email: z.string().email(),
})

type Schema = z.output<typeof schema>

const form = ref<Form<Schema>>()

const state = reactive({
  email: undefined,
})

watch(state, () => form.value?.clear())

const isMessageOpen = ref(false)
const message = ref<{
  title: string,
  content: string,
}>({
  title: '',
  content: '',
})

async function submit(event: FormSubmitEvent<Schema>) {
  const { data: { email } } = event

  try {
    await sendResetPasswordEmail(email)
  }
  catch {
    form.value!.setErrors([
      {
        path: 'email',
        message: true as any,
      },
      {
        path: 'errors',
        message: 'The e-mail you entered is invalid.',
      },
    ])
    return
  }

  message.value = {
    title: 'Password reset e-mail successfully sent',
    content: (
      'A password reset e-mail has just been sent to you. '
      + 'Follow the procedure to reset your password.'
    ),
  }
  isMessageOpen.value = true
}
</script>
