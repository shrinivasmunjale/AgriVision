'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/contexts/AuthContext'

export default function HomePage() {
  const router = useRouter()
  const { user, loading } = useAuth()

  useEffect(() => {
    // Always redirect to dashboard (whether logged in or not)
    if (!loading) {
      router.push('/dashboard')
    }
  }, [loading, router])

  return (
    <div className="flex items-center justify-center min-h-screen bg-surface-base">
      <div className="text-center">
        <div className="w-16 h-16 border-4 border-primary-400 border-t-transparent rounded-full animate-spin mx-auto"></div>
        <p className="mt-4 text-text-secondary">Loading AgriVision AI...</p>
      </div>
    </div>
  )
}
