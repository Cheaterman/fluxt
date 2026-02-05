export default function(filename?: string) {
  if (!filename) {
    return
  }

  const { app } = useRuntimeConfig()
  return `${app.baseURL}/api/files/${filename}`
}
