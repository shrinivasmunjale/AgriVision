'use client'

import { useState } from 'react'
import Link from 'next/link'
import { motion } from 'framer-motion'
import { ArrowLeft, KeyRound, Mail } from 'lucide-react'
import { useAuth } from '@/contexts/AuthContext'
import Logo from '@/components/ui/Logo'
import Button from '@/components/ui/Button'
import Card from '@/components/ui/Card'

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState('')
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')
  const [resetToken, setResetToken] = useState('')
  const { forgotPassword } = useAuth()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    setMessage('')
    try {
      const data = await forgotPassword(email)
      setMessage(data.message || 'If that email is registered, a reset link was generated.')
      if (data.reset_token) setResetToken(data.reset_token)
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
              <KeyRound className="w-7 h-7 text-primary-400" />
            </div>
            <h1 className="text-2xl font-bold mb-1">Forgot Password</h1>
            <p className="text-sm text-text-secondary">
              Enter your email and we’ll generate a reset token.
            </p>
          </div>

          {message && (
            <div className="mb-4 p-3 bg-status-successBg text-status-successText rounded-lg text-sm">
              {message}
              {resetToken && (
                <div className="mt-3">
                  <Link href={`/auth/reset-password?token=${encodeURIComponent(resetToken)}`}>
                    <Button size="sm" className="w-full">Continue to set new password</Button>
                  </Link>
                </div>
              )}
            </div>
          )}
          {error && !message && (
            <div className="mb-4 p-3 bg-status-dangerBg text-status-dangerText rounded-lg text-sm">{error}</div>
          )}

          {!message && (
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label htmlFor="email" className="block text-sm font-medium text-text-secondary mb-2">
                  Email
                </label>
                <div className="relative">
                  <Mail className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-text-secondary" />
                  <input
                    id="email"
                    type="email"
                    required
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="w-full pl-11 pr-4 py-3 bg-surface-base border border-border-subtle rounded-xl text-text-primary focus:outline-none focus:ring-2 focus:ring-primary-400"
                    placeholder="you@example.com"
                  />
                </div>
              </div>
              <Button type="submit" loading={loading} className="w-full">
                Send Reset Token
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