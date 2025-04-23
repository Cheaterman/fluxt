<template>
  <main class="flex flex-col gap-2">
    <h1
      class="text-lg font-bold w-full text-center"
    >
      Login
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
      <UCheckbox
        v-model="state.rememberMe"
        label="Remember me"
      />
      <ULink
        class="text-sm underline"
        to="/reset-password"
      >
        Forgotten password
      </ULink>
      <div
        class="flex flex-row gap-2 mt-2 justify-center"
      >
        <UButton
          label="Login"
          type="submit"
        />
      </div>
      <UFormGroup name="errors" />
    </UForm>
  </main>
</template>

<script setup lang="ts">
import { z } from 'zod'
import type { Form, FormSubmitEvent } from '#ui/types'

useSeoMeta({
  title: 'Login',
})

const { data: user } = await useAuth()

if (user.value) {
  await navigateTo('/')
}

const schema = z.object({
  email: z.union([z.string().email(), z.literal('admin')]),
  password: z.string().min(4),
  rememberMe: z.boolean(),
})

type Schema = z.output<typeof schema>

const form = ref<Form<Schema>>()

const state = reactive({
  email: undefined,
  password: undefined,
  rememberMe: false,
})

watch(state, () => form.value?.clear())

async function submit(event: FormSubmitEvent<Schema>) {
  const { data: { email: username, password, rememberMe } } = event

  try {
    await login({ username, password, rememberMe })
  }
  catch {
    form.value!.setErrors([
      {
        path: 'email',
        message: true as any,
      },
      {
        path: 'password',
        message: true as any,
      },
      {
        path: 'errors',
        message: 'Invalid email or password.',
      },
    ])
    return
  }
  return navigateTo('/')
}
</script>
