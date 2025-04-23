<template>
  <main class="flex flex-col gap-2">
    <header
      class="relative h-8"
    >
      <h1
        class="text-lg leading-8 font-bold w-full text-center"
      >
        Users
      </h1>
      <UButton
        class="absolute right-0 top-0"
        label="New user"
        to="/admin/users/new"
      />
    </header>
    <UInput
      v-model="searchText"
      class="w-1/4 mt-2 self-end"
      icon="i-heroicons-magnifying-glass"
      trailing
      placeholder="Search..."
    />
    <UTable
      :columns="columns"
      :rows="users"
      :empty-state="{
        icon: 'i-heroicons-user-group',
        label: searchText ? 'No users matching this search.' : 'No users.',
      }"
      :loading="pending"
    >
      <template #email-data="{ row: user }">
        <div class="flex flex-row items-center justify-between">
          {{ user.email }}
          <UButton
            class="-ml-10"
            icon="i-heroicons-envelope"
            :padded="false"
            variant="link"
            @click="confirmResendEmail(user)"
          />
        </div>
      </template>

      <template #role-data="{ row: user }">
        <RoleSelect
          v-model="user.role"
          @update:model-value="updateUser(user)"
        />
      </template>

      <template #enabled-data="{ row: user }">
        {{ user.enabled ? 'On' : 'Off' }}
      </template>

      <template #actions-data="{ row: user }">
        <div class="flex flex-row items-center gap-2">
          <UButton
            icon="i-heroicons-pencil-square"
            variant="link"
            :padded="false"
            :to="`/admin/users/edit/${user.id}`"
          />
          <UToggle
            v-model="user.enabled"
            size="xs"
            @update:model-value="updateUser(user)"
          />
          <UButton
            icon="i-heroicons-trash"
            variant="link"
            :padded="false"
            @click="confirmDelete(user)"
          />
        </div>
      </template>
    </UTable>
    <UModal
      v-model="isConfirmDeleteOpen"
    >
      <UCard>
        <template #header>
          <h2
            class="text-lg font-bold"
          >
            Confirm user deletion
          </h2>
        </template>

        <p>
          Are you sure you want to delete user
          {{ userBeingDeleted?.first_name }}
          {{ userBeingDeleted?.last_name }}?
        </p>

        <template #footer>
          <div class="flex flex-row justify-center gap-2">
            <UButton
              label="Cancel"
              color="gray"
              variant="outline"
              @click="isConfirmDeleteOpen = false"
            />
            <UButton
              label="Confirm"
              color="red"
              @click="submitDelete"
            />
          </div>
        </template>
      </UCard>
    </UModal>
    <UModal
      v-model="isConfirmResendEmailOpen"
    >
      <UCard>
        <template #header>
          <h2
            class="text-lg font-bold"
          >
            Confirm resend initialization email
          </h2>
        </template>

        <p v-if="!isConfirmResendEmailSent">
          Are you sure you want to resend the initialization email to
          {{ userBeingResentEmail?.email }}?
        </p>
        <p v-else>
          The reset email has been successfully sent to 
          {{ userBeingResentEmail?.email }}
        </p>

        <template #footer v-if="!isConfirmResendEmailSent">
          <div class="flex flex-row justify-center gap-2">
            <UButton
              label="Cancel"
              color="gray"
              variant="outline"
              @click="isConfirmResendEmailOpen = false"
            />
            <UButton
              label="Confirm"
              @click="submitResendEmail"
            />
          </div>
        </template>
        <template #footer v-else>
          <div class="flex flex-row justify-center">
            <UButton
              label="Ok"
              @click="isConfirmResendEmailOpen = false"
            />
          </div>
        </template>
      </UCard>
    </UModal>
  </main>
</template>

<script setup lang="ts">
import type { TableColumn } from '#ui/types'
import { FetchError } from 'ofetch'

definePageMeta({
  middleware: 'auth',
})

useSeoMeta({
  title: 'Users',
})

const columns: TableColumn[] = [
  {
    key: 'first_name',
    label: 'First name',
  },
  {
    key: 'last_name',
    label: 'Last name',
  },
  {
    key: 'email',
    label: 'E-mail',
  },
  {
    key: 'role',
    label: 'Role',
  },
  {
    key: 'creation_date',
    label: 'Creation date',
  },
  {
    key: 'enabled',
    label: 'Status',
  },
  {
    key: 'actions',
    rowClass: 'w-0 !p-0',
  },
]

const { data: _users, refresh, pending } = await useUsers()
const users = computed(
  () => (
    toValue(_users)
    ?.map((user) => {
      const date = new Date(user.creation_date)
      const creation_date = (
        `${date.getDate().toString().padStart(2, '0')}/`
        + `${(date.getMonth() + 1).toString().padStart(2, '0')}/`
        + date.getFullYear()
      )
      return {
        ...user,
        creation_date,
      }
    })
    .filter((user) => {
      const match = toValue(searchText).toLowerCase()

      if (!match) {
        return true
      }

      return JSON.stringify(user).toLowerCase().search(match) !== -1
    })
  )
)

const searchText = ref<string>('')

const isConfirmDeleteOpen = ref(false)
const userBeingDeleted = ref<User>()

function confirmDelete(user: User) {
  userBeingDeleted.value = user
  isConfirmDeleteOpen.value = true
}

async function submitDelete() {
  const user = toValue(userBeingDeleted)

  if (!user) {
    return
  }

  try {
    await deleteUser(user.id)
  }
  catch (error) {
    if (error instanceof FetchError) {
      return
    }
  }

  await refresh()
  isConfirmDeleteOpen.value = false
}

const isConfirmResendEmailOpen = ref(false)
const isConfirmResendEmailSent = ref(false)
const userBeingResentEmail = ref<User>()

function confirmResendEmail(user: User) {
  userBeingResentEmail.value = user
  isConfirmResendEmailSent.value = false
  isConfirmResendEmailOpen.value = true
}

async function submitResendEmail() {
  const user = toValue(userBeingResentEmail)

  if (!user) {
    return
  }

  try {
    await sendCreatedEmail(user.id)
  }
  catch (error) {
    if (error instanceof FetchError) {
      return
    }
  }

  isConfirmResendEmailSent.value = true
}

async function updateUser(_user: User) {
  const { id, creation_date, email, ...user } = _user

  try {
    await editUser(id, user)
  }
  finally {
    await refresh()
  }
}
</script>
