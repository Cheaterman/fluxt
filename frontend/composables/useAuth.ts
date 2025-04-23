export type AuthInfo = Omit<User, 'creation_date'>

export default () => {
  return useAPI<AuthInfo>('/auth')
}
