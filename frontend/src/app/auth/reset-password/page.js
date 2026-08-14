'use client'

import { Suspense, useState } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import Link from 'next/link'
import { motion } from 'framer-motion'
import { ArrowLeft, Lock } from 'lucide-react'
import { useAuth } from '@/contexts/AuthContext'
import Logo from '@/components/ui/Logo'
import Button from '@/components/ui/Button'
import Card from '@/components/ui/Card'

export default function ResetPasswordPage() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen flex items-center justify-center bg-surface-base">
          <div className="w-12 h-12 border-4 border-primary-400 border-t-transparent rounded-full animate-spin"></div>
        </div>
      }
    >
      <ResetPasswordContent />
    </Suspense>
  )
}

function ResetPasswordContent() {
  const [password, setPassword] = useState('')
  const [confirm, setConfirm] = useState('')
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')
  const router = useRouter()
  const searchParams = useSearchParams()
  const token = searchParams.get('token') || ''
  const { resetPassword } = useAuth()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    setMessage('')
    if (password !== confirm) {
      setError('Passwords do not match.')
      setLoading(false)
      return
    }
    if (!token) {
      setError('Missing reset token. Please request a new reset link.')
      setLoading(false)
      return
    }
    try {
      const data = await resetPassword(token, password)
      setMessage(data.message || 'Password updated successfully.')
      setTimeout(() => router.push('/auth/login'), 1800)
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Something went wrong')
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
        <div className="flex justify-center mb-6">
          <Logo />
        </div>
        <Card padded className="bg-surface-light text-text-inverse">
          <div className="text-center mb-6">
            <div className="w-14 h-14 rounded-2xl bg-primary-400/15 mx-auto flex items-center justify-center mb-4">
              <Lock className="w-7 h-7 text-primary-400" />
            </div>
            <h1 className="text-2xl font-bold mb-1">Set a new password</h1>
            <p className="text-sm text-text-secondary">Enter your new password below.</p>
          </div>

          {message && (
            <div className="mb-4 p-3 bg-status-successBg text-status-successText rounded-lg text-sm">
              {message} Redirecting to sign in...
            </div>
          )}
          {error && !message && (
            <div className="mb-4 p-3 bg-status-dangerBg text-status-dangerText rounded-lg text-sm">{error}</div>
          )}

          {!message && (
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label htmlFor="password" className="block text-sm font-medium text-text-secondary mb-2">
                  New Password
                </label>
                <div className="relative">
                  <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-text-secondary" />
                  <input
                    id="password"
                    type="password"
                    required
                    minLength={6}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="w-full pl-11 pr-4 py-3 bg-surface-base border border-border-subtle rounded-xl text-text-primary focus:outline-none focus:ring-2 focus:ring-primary-400"
                    placeholder="At least 6 characters"
                  />
                </div>
              </div>
              <div>
                <label htmlFor="confirm" className="block text-sm font-medium text-text-secondary mb-2">
                  Confirm Password
                </label>
                <div className="relative">
                  <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-text-secondary" />
                  <input
                    id="confirm"
                    type="password"
                    required
                    minLength={6}
                    value={confirm}
                    onChange={(e) => setConfirm(e.target.value)}
                    className="w-full pl-11 pr-4 py-3 bg-surface-base border border-border-subtle rounded-xl text-text-primary focus:outline-none focus:ring-2 focus:ring-primary-400"
                    placeholder="Re-enter password"
                  />
                </div>
              </div>
              <Button type="submit" loading={loading} className="w-full">
                Update Password
              </Button>
            </form>
          )}

          <div className="mt-6 text-center">
            <Link href="/auth/login" className="inline-flex items-center gap-1.5 text-sm text-primary-500 font-medium hover:underline">
              <ArrowLeft className="w-4 h-4" /> Back to sign in
            </Link>
          </div>
        </Card>
      </motion.div>
    </div>
  )
}