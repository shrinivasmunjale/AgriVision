'use client'

import { createContext, useContext, useEffect, useState } from 'react'
import axios from 'axios'

const AuthContext = createContext({})

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider')
  }
  return context
}

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null)
  const [session, setSession] = useState(null)
  const [loading, setLoading] = useState(true)
  const [profile, setProfile] = useState(null)

  useEffect(() => {
    // Check for existing token in localStorage
    const token = localStorage.getItem('access_token')
    if (token) {
      fetchUserProfile(token)
    } else {
      setLoading(false)
    }
  }, [])

  const fetchUserProfile = async (token) => {
    try {
      const response = await axios.get(`${API_URL}/auth/me`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      })
      setProfile(response.data)
      setUser(response.data)
      setSession({ access_token: token })
      setLoading(false)
    } catch (error) {
      console.error('Failed to fetch user profile:', error)
      localStorage.removeItem('access_token')
      setProfile(null)
      setUser(null)
      setSession(null)
      setLoading(false)
    }
  }

  const signIn = async (email, password) => {
    try {
      // Send JSON payload instead of form data
      const response = await axios.post(`${API_URL}/auth/login`, {
        email,
        password
      }, {
        headers: {
          'Content-Type': 'application/json',
        },
      })

      const { access_token } = response.data
      localStorage.setItem('access_token', access_token)
      
      await fetchUserProfile(access_token)
      
      return { user: profile, session: { access_token } }
    } catch (error) {
      console.error('Login error:', error.response?.data || error.message)
      throw new Error(error.response?.data?.detail || 'Login failed')
    }
  }

  const signUp = async (email, password, metadata) => {
    try {
      const response = await axios.post(`${API_URL}/auth/register`, {
        email,
        password,
        full_name: metadata?.full_name || '',
        role: metadata?.role || 'farmer',
        farm_name: metadata?.farm_name || '',
        phone: metadata?.phone || '',
      })

      // After registration, automatically sign in
      return await signIn(email, password)
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Registration failed')
    }
  }

  const signOut = async () => {
    localStorage.removeItem('access_token')
    setProfile(null)
    setUser(null)
    setSession(null)
  }

  const getAccessToken = async () => {
    return localStorage.getItem('access_token')
  }

  const value = {
    signIn,
    signUp,
    signOut,
    user,
    session,
    loading,
    profile,
    getAccessToken,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}
