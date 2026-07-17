'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/contexts/AuthContext'
import { authAPI } from '@/lib/api'
import Link from 'next/link'
import { motion } from 'framer-motion'

export default function LoginPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const router = useRouter()
  const { signIn } = useAuth()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')

    try {
      await signIn(email, password)
      router.push('/dashboard')
    } catch (err) {
      setError(err.message || 'Failed to sign in')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-surface-base p-4">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-md"
      >
        <div className="bg-surface-light rounded-2xl p-8 shadow-lg">
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-text-inverse mb-2">
              Welcome Back
            </h1>
            <p className="text-gray-600">Sign in to AgriVision AI</p>
          </div>

          {error && (
            <div className="mb-4 p-3 bg-status-dangerBg text-status-dangerText rounded-lg text-sm">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-text-inverse mb-2">
                Email
              </label>
              <input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                className="w-full px-4 py-3 bg-white border border-border-light rounded-xl text-text-inverse focus:outline-none focus:ring-2 focus:ring-primary-400"
                placeholder="you@example.com"
              />
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-medium text-text-inverse mb-2">
                Password
              </label>
              <input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                className="w-full px-4 py-3 bg-white border border-border-light rounded-xl text-text-inverse focus:outline-none focus:ring-2 focus:ring-primary-400"
                placeholder="••••••••"
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full py-3 bg-primary text-white rounded-full font-semibold hover:bg-primary-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Signing in...' : 'Sign In'}
            </button>
          </form>

          <div className="mt-6 text-center">
            <p className="text-sm text-gray-600">
              Don't have an account?{' '}
              <Link href="/auth/register" className="text-primary-500 font-semibold hover:underline">
                Sign up
              </Link>
            </p>
          </div>
        </div>
      </motion.div>
    </div>
  )
}
