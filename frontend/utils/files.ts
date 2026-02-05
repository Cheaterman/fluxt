interface UploadResponse {
  filename: string
}

export async function uploadFile(file: File) {
  const { $api } = useNuxtApp()

  const formData = new FormData()
  formData.append('file', file)

  const response = await $api<UploadResponse>('/files', {
    method: 'POST',
    body: formData,
  })

  return response
}

export async function deleteFile(filename: string) {
  const { $api } = useNuxtApp()

  return await $api<void>(
    `/files/${filename}`,
    { method: 'DELETE' }
  )
}
