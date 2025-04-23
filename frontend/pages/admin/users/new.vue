<template>
  <main class="flex flex-col gap-2">
    <header
      class="relative h-8"
    >
      <UButton
        class="absolute left-0 top-0"
        label="Back"
        icon="i-heroicons-arrow-uturn-left-16-solid"
        @click="$router.back()"
      />
      <h1
        class="text-lg leading-8 font-bold w-full text-center"
      >
        New user
      </h1>
    </header>
    <UForm
      class="flex flex-col gap-2"
      ref="form"
      :schema="schema"
      :state="state"
      @submit="submit"
    >
      <UFormGroup
        name="first_name"
        label="First name"
        required
      >
        <UInput
          v-model="state.first_name"
        />
      </UFormGroup>
      <UFormGroup
        name="last_name"
        label="Last name"
        required
      >
        <UInput
          v-model="state.last_name"
        />
      </UFormGroup>
      <UFormGroup
        name="role"
        label="Role"
        required
      >
        <RoleSelect
          v-model="state.role"
        />
      </UFormGroup>
      <UFormGroup
        name="email"
        label="E-mail"
        required
      >
        <UInput
          v-model="state.email"
        />
      </UFormGroup>
      <UFormGroup name="errors" />
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
          label="Create"
          type="submit"
        />
      </div>
    </UForm>
  </main>
</template>

<script setup lang="ts">
import { z } from 'zod'
import { FetchError } from 'ofetch'
import type { Form, FormSubmitEvent } from '#ui/types'

definePageMeta({
  middleware: 'auth',
})

useSeoMeta({
  title: 'New user',
})

const schema = z.object({
  email: z.string().email(),
  first_name: z.string().min(1),
  last_name: z.string().min(1),
  role: z.enum(ROLES),
})

type Schema = z.output<typeof schema>

const form = ref<Form<Schema>>()

const state = reactive({
  email: undefined,
  first_name: undefined,
  last_name: undefined,
  role: 'user',
})

watch(state, () => form.value?.clear('errors'))

async function submit(event: FormSubmitEvent<Schema>) {
  const { data } = event

  try {
    await createUser(data)
  }
  catch (error) {
    if (error instanceof FetchError) {
      if (error.status === 409) {
        form.value!.setErrors([
          {
            path: 'errors',
            message: 'A user with this e-mail address already exists.',
          }
        ])
        return
      }
    }
    form.value!.setErrors([
      {
        path: 'errors',
        message: 'An unknown error occured. Please try again later.',
      }
    ])
    console.error({ error })
    return
  }

  return navigateTo('/admin/users')
}
</script>
