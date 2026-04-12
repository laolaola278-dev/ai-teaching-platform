import React, { createContext, useContext, useEffect, useMemo, useState } from 'react'

type User = {
  id?: string
  username?: string
  email?: string
  roles?: string[]
}

type AuthContextType = {
  user: User | null
  accessToken: string | null
  login: (username: string, password: string) => Promise<boolean>
  logout: () => void
  register: (payload: { username: string; email: string; password: string }) => Promise<boolean>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export const useAuth = (): AuthContextType => {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null)
  const [accessToken, setAccessToken] = useState<string | null>(null)

  useEffect(() => {
    const t = localStorage.getItem('access_token')
    const u = localStorage.getItem('user')
    if (t && u) {
      setAccessToken(t)
      try{ setUser(JSON.parse(u)) } catch {}
    }
  }, [])

  const login = async (username: string, password: string): Promise<boolean> => {
    // Call login API
    const resp = await fetch('/api/v1/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password }),
    })
    if (!resp.ok) return false
    const data = await resp.json()
    const token = data?.access_token
    if (token) {
      setAccessToken(token)
      localStorage.setItem('access_token', token)
      const userObj = { id: data?.user_id ?? '', username }
      setUser(userObj as User)
      localStorage.setItem('user', JSON.stringify(userObj))
      return true
    }
    return false
  }

  const logout = (): void => {
    setAccessToken(null)
    setUser(null)
    localStorage.removeItem('access_token')
    localStorage.removeItem('user')
  }

  const register = async (payload: { username: string; email: string; password: string }): Promise<boolean> => {
    const resp = await fetch('/api/v1/auth/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })
    return resp.ok
  }

  const value = useMemo(() => ({ user, accessToken, login, logout, register }), [user, accessToken])
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}
