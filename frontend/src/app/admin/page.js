'use client'

import { useAuth } from '@/contexts/AuthContext'
import { useRouter } from 'next/navigation'
import { useEffect } from 'react'
import { useQuery } from '@tanstack/react-query'
import { adminAPI } from '@/lib/api'
import Layout from '@/components/Layout'
import { Users, Activity, TrendingUp, Database } from 'lucide-react'
import { motion } from 'framer-motion'

export default function AdminPage() {
  const { user, loading, getAccessToken, profile } = useAuth()
  const router = useRouter()

  useEffect(() => {
    if (!loading && !user) {
      router.push('/auth/login')
    } else if (!loading && profile && profile.role !== 'admin') {
      router.push('/dashboard')
    }
  }, [user, loading, profile, router])

  const { data: analytics, isLoading } = useQuery({
    queryKey: ['admin-analytics'],
    queryFn: async () => {
      const token = await getAccessToken()
      const response = await adminAPI.getAnalytics(token)
      return response.data
    },
    enabled: !!user && profile?.role === 'admin',
  })

  if (loading || !user || !profile || profile.role !== 'admin') {
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
        >
          <h1 className="text-3xl font-bold text-text-primary mb-2">
            Admin Dashboard
          </h1>
          <p className="text-text-secondary mb-8">
            Platform analytics and management
          </p>

          {isLoading ? (
            <div className="text-center py-12">
              <div className="w-12 h-12 border-4 border-primary-400 border-t-transparent rounded-full animate-spin mx-auto"></div>
            </div>
          ) : analytics ? (
            <>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.1 }}
                  className="bg-surface-card rounded-2xl p-6 border border-border-subtle"
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-text-secondary text-sm mb-1">Total Users</p>
                      <p className="text-3xl font-bold text-text-primary">
                        {analytics.total_users}
                      </p>
                    </div>
                    <div className="w-12 h-12 bg-primary-400/20 rounded-xl flex items-center justify-center">
                      <Users className="w-6 h-6 text-primary-400" />
                    </div>
                  </div>
                </motion.div>

                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.2 }}
                  className="bg-surface-card rounded-2xl p-6 border border-border-subtle"
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-text-secondary text-sm mb-1">Total Scans</p>
                      <p className="text-3xl font-bold text-text-primary">
                        {analytics.total_predictions}
                      </p>
                    </div>
                    <div className="w-12 h-12 bg-primary-400/20 rounded-xl flex items-center justify-center">
                      <Activity className="w-6 h-6 text-primary-400" />
                    </div>
                  </div>
                </motion.div>

                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.3 }}
                  className="bg-surface-card rounded-2xl p-6 border border-border-subtle"
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-text-secondary text-sm mb-1">Avg Confidence</p>
                      <p className="text-3xl font-bold text-text-primary">
                        {analytics.average_confidence}%
                      </p>
                    </div>
                    <div className="w-12 h-12 bg-primary-400/20 rounded-xl flex items-center justify-center">
                      <TrendingUp className="w-6 h-6 text-primary-400" />
                    </div>
                  </div>
                </motion.div>

                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.4 }}
                  className="bg-surface-card rounded-2xl p-6 border border-border-subtle"
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-text-secondary text-sm mb-1">Diseases</p>
                      <p className="text-3xl font-bold text-text-primary">
                        {analytics.disease_distribution?.length || 0}
                      </p>
                    </div>
                    <div className="w-12 h-12 bg-primary-400/20 rounded-xl flex items-center justify-center">
                      <Database className="w-6 h-6 text-primary-400" />
                    </div>
                  </div>
                </motion.div>
              </div>

              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.5 }}
                className="bg-surface-card rounded-2xl p-6 border border-border-subtle mb-8"
              >
                <h2 className="text-xl font-bold text-text-primary mb-4">
                  Disease Distribution
                </h2>
                <div className="space-y-3">
                  {analytics.disease_distribution?.map((item, index) => {
                    const total = analytics.total_predictions
                    const percentage = total > 0 ? ((item.count / total) * 100).toFixed(1) : 0
                    return (
                      <div key={index}>
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-text-primary">{item.disease}</span>
                          <span className="text-text-secondary text-sm">
                            {item.count} ({percentage}%)
                          </span>
                        </div>
                        <div className="w-full bg-surface-base rounded-full h-2">
                          <div
                            className="bg-primary-400 h-2 rounded-full"
                            style={{ width: `${percentage}%` }}
                          />
                        </div>
                      </div>
                    )
                  })}
                </div>
              </motion.div>

              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.6 }}
                className="bg-surface-card rounded-2xl p-6 border border-border-subtle"
              >
                <h2 className="text-xl font-bold text-text-primary mb-4">
                  Recent Activity
                </h2>
                {analytics.recent_audits && analytics.recent_audits.length > 0 ? (
                  <div className="space-y-3">
                    {analytics.recent_audits.map((audit, index) => (
                      <div
                        key={index}
                        className="flex items-center justify-between p-3 bg-surface-base rounded-lg"
                      >
                        <div>
                          <p className="text-text-primary">
                            <span className="font-semibold">{audit.action}</span> {audit.entity}
                          </p>
                          <p className="text-text-secondary text-xs">
                            {new Date(audit.timestamp).toLocaleString()}
                          </p>
                        </div>
                        <span className="text-text-secondary text-xs">
                          ID: {audit.entity_id}
                        </span>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-text-secondary text-center py-4">No recent activity</p>
                )}
              </motion.div>
            </>
          ) : null}
        </motion.div>
      </div>
    </Layout>
  )
}
