'use client'

import { useState } from 'react'
import { Lock } from 'lucide-react'
import { useAuth } from '@/contexts/AuthContext'
import Button from '@/components/ui/Button'

export default function ChangePasswordForm() {
  const { changePassword } = useAuth()
  const [oldPassword, setOldPassword] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setMessage('')
    if (newPassword !== confirmPassword) {
      setError('New passwords do not match.')
      return
    }
    if (newPassword.length < 6) {
      setError('Password must be at least 6 characters.')
      return
    }
    setLoading(true)
    try {
      const data = await changePassword(oldPassword, newPassword)
      setMessage(data.message || 'Password changed successfully.')
      setOldPassword('')
      setNewPassword('')
      setConfirmPassword('')
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Failed to change password')
    } finally {
      setLoading(false)
    }
  }

  const fields = [
    { key: 'old', label: 'Current Password', value: oldPassword, set: setOldPassword },
    { key: 'new', label: 'New Password', value: newPassword, set: setNewPassword },
    { key: 'confirm', label: 'Confirm New Password', value: confirmPassword, set: setConfirmPassword },
  ]

  return (
    <div className="bg-surface-card rounded-2xl p-6 border border-border-subtle">
      {message && (
        <div className="mb-4 p-3 bg-status-successBg text-status-successText rounded-lg text-sm">{message}</div>
      )}
      {error && (
        <div className="mb-4 p-3 bg-status-dangerBg text-status-dangerText rounded-lg text-sm">{error}</div>
      )}
      <form onSubmit={handleSubmit} className="space-y-4">
        {fields.map((f) => (
          <div key={f.key}>
            <label className="block text-sm font-medium text-text-secondary mb-2">{f.label}</label>
            <div className="relative">
              <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-text-secondary" />
              <input
                type="password"
                required
                minLength={6}
                value={f.value}
                onChange={(e) => f.set(e.target.value)}
                className="w-full pl-11 pr-4 py-3 bg-surface-base border border-border-subtle rounded-xl text-text-primary focus:outline-none focus:ring-2 focus:ring-primary-400"
                placeholder={f.key === 'old' ? 'Enter current password' : 'At least 6 characters'}
              />
            </div>
          </div>
        ))}
        <Button type="submit" loading={loading} className="w-full">
          Update Password
        </Button>
      </form>
    </div>
  )
}