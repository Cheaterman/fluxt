export async function createUser(
  user: Omit<User, 'id' | 'creation_date' | 'enabled'>
) {
  const { $api } = useNuxtApp()
  return $api<{ id: string }>('/users', {
    method: 'POST',
    body: user,
  })
}

export async function sendCreatedEmail(id: User['id']) {
  const { $api } = useNuxtApp()
  return $api<''>(`/users/${id}/send-created-email`, { method: 'POST' })
}

export async function getPasswordState(token: string) {
  const { $api } = useNuxtApp()
  return $api<''>(`/set-password/${token}`)
}

export async function setPassword(token: string, password: string) {
  const { $api } = useNuxtApp()
  return $api<''>(`/set-password/${token}`, {
    method: 'POST',
    body: { password },
  })
}

export async function editUser(
  id: User['id'],
  user: Partial<Omit<User, 'id' | 'creation_date' | 'email'>>,
) {
  const { $api } = useNuxtApp()
  return $api<User>(`/users/${id}`, {
    method: 'PUT',
    body: user,
  })
}

export async function sendResetPasswordEmail(email: User['email']) {
  const { $api } = useNuxtApp()
  return $api<User>(`/reset-password/${email}`)
}

export async function resetPassword(token: string, password: string) {
  const { $api } = useNuxtApp()
  return $api<User>(`/reset-password/${token}`, {
    method: 'POST',
    body: { password },
  })
}

export async function deleteUser(id: string) {
  const { $api } = useNuxtApp()
  return $api<''>(`/users/${id}`, { method: 'DELETE' })
}
