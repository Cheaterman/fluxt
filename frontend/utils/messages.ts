export async function sendMessage(message: string) {
  const { $api } = useNuxtApp()
  return $api<{ id: string }>('/messages', {
    method: 'POST',
    body: { text: message },
  })
}

export async function deleteMessage(id: string) {
  const { $api } = useNuxtApp()
  return $api<''>(`/messages/${id}`, { method: 'DELETE' })
}
