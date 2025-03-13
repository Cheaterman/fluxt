const { $api } = useNuxtApp()

export async function login(
  { username, password }:
  { username: string, password: string }
) {
  return $api<''>('/auth', { headers: {
    'Authorization': 'Basic ' + btoa(`${username}:${password}`),
  }})
}

export async function logout() {
  return $api<''>('/deauth')
}
