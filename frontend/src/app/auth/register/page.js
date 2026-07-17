'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/contexts/AuthContext'
import { authAPI } from '@/lib/api'
import Link from 'next/link'
import { motion } from 'framer-motion'

export default function RegisterPage() {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    name: '',
    farmName: '',
    phone: '',
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const router = useRouter()
  const { signUp, getAccessToken } = useAuth()

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    })
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')

    try {
      // Sign up with Supabase
      await signUp(formData.email, formData.password, {
        name: formData.name,
      })

      // Get access token
      const token = await getAccessToken()

      // Register in backend
      await authAPI.register(
        {
          name: formData.name,
          farm_name: formData.farmName,
          phone: formData.phone,
        },
        token
      )

      router.push('/dashboard')
    } catch (err) {
      setError(err.message || 'Failed to create account')
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
              Join AgriVision AI
            </h1>
            <p className="text-gray-600">Create your account</p>
          </div>

          {error && (
            <div className="mb-4 p-3 bg-status-dangerBg text-status-dangerText rounded-lg text-sm">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label htmlFor="name" className="block text-sm font-medium text-text-inverse mb-2">
                Full Name
              </label>
              <input
                id="name"
                name="name"
                type="text"
                value={formData.name}
                onChange={handleChange}
                required
                className="w-full px-4 py-3 bg-white border border-border-light rounded-xl text-text-inverse focus:outline-none focus:ring-2 focus:ring-primary-400"
                placeholder="John Doe"
              />
            </div>

            <div>
              <label htmlFor="email" className="block text-sm font-medium text-text-inverse mb-2">
                Email
              </label>
              <input
                id="email"
                name="email"
                type="email"
                value={formData.email}
                onChange={handleChange}
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
                name="password"
                type="password"
                value={formData.password}
                onChange={handleChange}
                required
                className="w-full px-4 py-3 bg-white border border-border-light rounded-xl text-text-inverse focus:outline-none focus:ring-2 focus:ring-primary-400"
                placeholder="••••••••"
              />
            </div>

            <div>
              <label htmlFor="farmName" className="block text-sm font-medium text-text-inverse mb-2">
                Farm Name (Optional)
              </label>
              <input
                id="farmName"
                name="farmName"
                type="text"
                value={formData.farmName}
                onChange={handleChange}
                className="w-full px-4 py-3 bg-white border border-border-light rounded-xl text-text-inverse focus:outline-none focus:ring-2 focus:ring-primary-400"
                placeholder="My Farm"
              />
            </div>

            <div>
              <label htmlFor="phone" className="block text-sm font-medium text-text-inverse mb-2">
                Phone (Optional)
              </label>
              <input
                id="phone"
                name="phone"
                type="tel"
                value={formData.phone}
                onChange={handleChange}
                className="w-full px-4 py-3 bg-white border border-border-light rounded-xl text-text-inverse focus:outline-none focus:ring-2 focus:ring-primary-400"
                placeholder="+1234567890"
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full py-3 bg-primary text-white rounded-full font-semibold hover:bg-primary-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Creating account...' : 'Create Account'}
            </button>
          </form>

          <div className="mt-6 text-center">
            <p className="text-sm text-gray-600">
              Already have an account?{' '}
              <Link href="/auth/login" className="text-primary-500 font-semibold hover:underline">
                Sign in
              </Link>
            </p>
          </div>
        </div>
      </motion.div>
    </div>
  )
}
