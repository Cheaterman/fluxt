export async function login(
  { username, password, rememberMe }:
  { username: string, password: string, rememberMe: boolean }
) {
  const { $api } = useNuxtApp()
  return $api<AuthInfo>('/auth', { headers: {
    'Authorization': 'Basic ' + btoa(`${username}:${password}`),
    'Fluxt-Remember-Me': rememberMe.toString(),
  }})
}

export async function logout() {
  const { $api } = useNuxtApp()
  return $api<''>('/deauth')
}
