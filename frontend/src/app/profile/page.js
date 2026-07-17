'use client'

import { useAuth } from '@/contexts/AuthContext'
import { useRouter } from 'next/navigation'
import { useEffect } from 'react'
import Layout from '@/components/Layout'
import { User, Mail, Building2, Phone, Shield, LogOut } from 'lucide-react'
import { motion } from 'framer-motion'

export default function ProfilePage() {
  const { user, loading, profile, signOut } = useAuth()
  const router = useRouter()

  useEffect(() => {
    if (!loading && !user) {
      router.push('/auth/login')
    }
  }, [user, loading, router])

  const handleSignOut = async () => {
    await signOut()
    router.push('/auth/login')
  }

  if (loading || !user || !profile) {
    return (
      <Layout>
        <div className="flex items-center justify-center min-h-screen">
          <div className="w-16 h-16 border-4 border-primary-400 border-t-transparent rounded-full animate-spin"></div>
        </div>
      </Layout>
    )
  }

  return (
    <Layout>
      <div className="p-4 lg:p-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="max-w-2xl mx-auto"
        >
          <h1 className="text-3xl font-bold text-text-primary mb-2">Profile</h1>
          <p className="text-text-secondary mb-8">Manage your account information</p>

          <div className="bg-surface-card rounded-2xl p-6 border border-border-subtle mb-6">
            <div className="flex items-center gap-4 mb-6">
              <div className="w-20 h-20 bg-primary-400/20 rounded-full flex items-center justify-center">
                <User className="w-10 h-10 text-primary-400" />
              </div>
              <div>
                <h2 className="text-2xl font-bold text-text-primary">{profile.name}</h2>
                <span
                  className={`inline-block px-3 py-1 rounded-full text-xs font-medium mt-2 ${
                    profile.role === 'Admin'
                      ? 'bg-accent/20 text-accent'
                      : 'bg-primary-400/20 text-primary-400'
                  }`}
                >
                  {profile.role}
                </span>
              </div>
            </div>

            <div className="space-y-4">
              <div className="flex items-center gap-3 p-4 bg-surface-base rounded-lg">
                <Mail className="w-5 h-5 text-text-secondary" />
                <div>
                  <p className="text-text-secondary text-sm">Email</p>
                  <p className="text-text-primary">{profile.email}</p>
                </div>
              </div>

              {profile.farm_name && (
                <div className="flex items-center gap-3 p-4 bg-surface-base rounded-lg">
                  <Building2 className="w-5 h-5 text-text-secondary" />
                  <div>
                    <p className="text-text-secondary text-sm">Farm Name</p>
                    <p className="text-text-primary">{profile.farm_name}</p>
                  </div>
                </div>
              )}

              {profile.phone && (
                <div className="flex items-center gap-3 p-4 bg-surface-base rounded-lg">
                  <Phone className="w-5 h-5 text-text-secondary" />
                  <div>
                    <p className="text-text-secondary text-sm">Phone</p>
                    <p className="text-text-primary">{profile.phone}</p>
                  </div>
                </div>
              )}

              <div className="flex items-center gap-3 p-4 bg-surface-base rounded-lg">
                <Shield className="w-5 h-5 text-text-secondary" />
                <div>
                  <p className="text-text-secondary text-sm">Member Since</p>
                  <p className="text-text-primary">
                    {new Date(profile.created_at).toLocaleDateString('en-US', {
                      month: 'long',
                      day: 'numeric',
                      year: 'numeric',
                    })}
                  </p>
                </div>
              </div>
            </div>
          </div>

          <button
            onClick={handleSignOut}
            className="w-full flex items-center justify-center gap-2 py-3 bg-red-500 text-white rounded-full font-semibold hover:bg-red-600 transition-colors"
          >
            <LogOut className="w-5 h-5" />
            Sign Out
          </button>
        </motion.div>
      </div>
    </Layout>
  )
}
