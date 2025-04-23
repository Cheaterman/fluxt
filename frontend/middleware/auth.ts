export default defineNuxtRouteMiddleware(async (to) => {
  const { data: authInfo } = await useAuth()
  const user = toValue(authInfo)

  if (!user) {
    return navigateTo('/login')
  }

  if (to.path.startsWith('/admin/') && user.role !== 'administrator') {
    throw createError({
      status: 403,
      message: 'You are not allowed to view this page.',
      fatal: true,
    })
  }
})
