export type RoleValue =
  | 'administrator'
  | 'user'

export interface AuthInfo {
  id: string
  name: string
  role: RoleValue
}

export default () => {
  return useAPI<AuthInfo>('/auth')
}
