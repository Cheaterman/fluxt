export default defineEventHandler((event) => {
  if (!event.path.startsWith('/api/')) {
    return
  }
  const { req } = event.node
  const target = `http://proxy${req.originalUrl}`
  return proxyRequest(event, target)
})
