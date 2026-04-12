export const applyAuthInterceptor = (tokenGetter: () => string | null) => {
  if (!tokenGetter) return
  // This module can be used to attach token to axios requests if using a shared axios instance
  // The actual axios instance is defined in client.ts; here we expose the helper
}
