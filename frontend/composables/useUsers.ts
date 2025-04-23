export const ROLES = [
  'administrator',
  'user',
] as const
export type Role = typeof ROLES[number]

export const ROLE_NAMES: Record<Role, string> = {
  administrator: 'Administrator',
  user: 'User',
}

export interface User {
  id: string
  creation_date: string
  email: string
  first_name: string
  last_name: string
  role: Role
  enabled: boolean
}

export default async function() {
  return useAPI('/users', {
    transform: (data: { users: User[] }) => data.users,
  } as { transform: (data: any) => User[] })
}

export async function useUser(id: User['id']) {
  return useAPI<User>(`/users/${id}`)
}
