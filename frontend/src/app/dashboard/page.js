'use client'

import { useAuth } from '@/contexts/AuthContext'
import { useRouter } from 'next/navigation'
import { useEffect } from 'react'
import { useQuery } from '@tanstack/react-query'
import { predictionsAPI } from '@/lib/api'
import Layout from '@/components/Layout'
import { Camera, TrendingUp, CheckCircle, AlertTriangle } from 'lucide-react'
import { motion } from 'framer-motion'
import Link from 'next/link'

export default function DashboardPage() {
  const { user, loading, getAccessToken, profile } = useAuth()
  const router = useRouter()

  useEffect(() => {
    if (!loading && !user) {
      router.push('/auth/login')
    }
  }, [user, loading, router])

  const { data: predictions, isLoading } = useQuery({
    queryKey: ['predictions'],
    queryFn: async () => {
      const token = await getAccessToken()
      const response = await predictionsAPI.getAll({ limit: 5 }, token)
      return response.data
    },
    enabled: !!user,
  })

  if (loading || !user) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-primary-400 border-t-transparent rounded-full animate-spin mx-auto"></div>
          <p className="mt-4 text-text-secondary">Loading...</p>
        </div>
      </div>
    )
  }

  const healthyCount = predictions?.filter(p => p.disease_name === 'Healthy').length || 0
  const totalCount = predictions?.length || 0
  const healthyRatio = totalCount > 0 ? ((healthyCount / totalCount) * 100).toFixed(1) : 0

  return (
    <Layout>
      <div className="p-4 lg:p-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <h1 className="text-3xl font-bold text-text-primary mb-2">
            Welcome back, {profile?.name || 'Farmer'}!
          </h1>
          <p className="text-text-secondary">
            Monitor your crop health and get AI-powered insights
          </p>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="bg-surface-card rounded-2xl p-6 border border-border-subtle"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-text-secondary text-sm mb-1">Total Analyzed</p>
                <p className="text-3xl font-bold text-text-primary">{totalCount}</p>
              </div>
              <div className="w-12 h-12 bg-primary-400/20 rounded-xl flex items-center justify-center">
                <TrendingUp className="w-6 h-6 text-primary-400" />
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
                <p className="text-text-secondary text-sm mb-1">Healthy Ratio</p>
                <p className="text-3xl font-bold text-text-primary">{healthyRatio}%</p>
              </div>
              <div className="w-12 h-12 bg-primary-400/20 rounded-xl flex items-center justify-center">
                <CheckCircle className="w-6 h-6 text-primary-400" />
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
                <p className="text-text-secondary text-sm mb-1">Issues Found</p>
                <p className="text-3xl font-bold text-text-primary">{totalCount - healthyCount}</p>
              </div>
              <div className="w-12 h-12 bg-accent/20 rounded-xl flex items-center justify-center">
                <AlertTriangle className="w-6 h-6 text-accent" />
              </div>
            </div>
          </motion.div>
        </div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="mb-8"
        >
          <Link
            href="/scan"
            className="flex items-center justify-center gap-3 w-full py-4 bg-primary text-white rounded-full font-semibold hover:bg-primary-600 transition-colors"
          >
            <Camera className="w-5 h-5" />
            Scan Tomato Leaves Now
          </Link>
        </motion.div>

        {/* Drone Imagery Showcase */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
          className="mb-8"
        >
          <div className="bg-gradient-to-r from-primary-400 to-primary-600 rounded-2xl p-6 text-white">
            <div className="flex items-start justify-between mb-4">
              <div>
                <h2 className="text-2xl font-bold mb-2">🚁 Drone-Captured Analysis</h2>
                <p className="text-white/80">
                  Upload aerial images captured by agricultural drones for comprehensive field analysis
                </p>
              </div>
            </div>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
              {[
                { 
                  url: 'https://images.unsplash.com/photo-1464226184884-fa280b87c399?w=400&h=300&fit=crop',
                  label: 'Aerial View'
                },
                { 
                  url: 'https://images.unsplash.com/photo-1530836369250-ef72a3f5cda8?w=400&h=300&fit=crop',
                  label: 'Crop Field'
                },
                { 
                  url: 'https://images.unsplash.com/photo-1625246333195-78d9c38ad449?w=400&h=300&fit=crop',
                  label: 'Farm Overview'
                },
                { 
                  url: 'https://images.unsplash.com/photo-1592982537447-7440770cbfc9?w=400&h=300&fit=crop',
                  label: 'Tomato Rows'
                }
              ].map((img, idx) => (
                <div key={idx} className="relative rounded-lg overflow-hidden group">
                  <img
                    src={img.url}
                    alt={img.label}
                    className="w-full h-32 object-cover group-hover:scale-110 transition-transform duration-300"
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent flex items-end p-2">
                    <span className="text-white text-xs font-medium">{img.label}</span>
                  </div>
                </div>
              ))}
            </div>
            <div className="flex items-center gap-3 text-sm text-white/90">
              <div className="flex items-center gap-1">
                <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
                <span>High-resolution imagery</span>
              </div>
              <div className="flex items-center gap-1">
                <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
                <span>Multi-acre coverage</span>
              </div>
              <div className="flex items-center gap-1">
                <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
                <span>AI-powered detection</span>
              </div>
            </div>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
        >
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-bold text-text-primary">Recent Activity</h2>
            <Link href="/history" className="text-primary-400 text-sm hover:underline">
              View All
            </Link>
          </div>

          {isLoading ? (
            <div className="text-center py-8">
              <div className="w-8 h-8 border-4 border-primary-400 border-t-transparent rounded-full animate-spin mx-auto"></div>
            </div>
          ) : predictions && predictions.length > 0 ? (
            <div className="space-y-3">
              {predictions.map((prediction, index) => (
                <Link
                  key={prediction.id}
                  href={`/history/${prediction.id}`}
                  className="block"
                >
                  <motion.div
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.6 + index * 0.1 }}
                    className="bg-surface-card rounded-xl p-4 border border-border-subtle hover:border-primary-400 transition-colors"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <span
                            className={`px-3 py-1 rounded-full text-xs font-medium ${
                              prediction.disease_name === 'Healthy'
                                ? 'bg-status-successBg text-status-successText'
                                : 'bg-status-dangerBg text-status-dangerText'
                            }`}
                          >
                            {prediction.disease_name || 'Unknown'}
                          </span>
                          <span className="text-text-secondary text-sm">
                            {(prediction.confidence_score * 100).toFixed(1)}% confidence
                          </span>
                        </div>
                        <p className="text-text-secondary text-xs">
                          {new Date(prediction.created_at).toLocaleDateString('en-US', {
                            month: 'short',
                            day: 'numeric',
                            year: 'numeric',
                            hour: '2-digit',
                            minute: '2-digit',
                          })}
                        </p>
                      </div>
                      <svg
                        className="w-5 h-5 text-text-secondary"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M9 5l7 7-7 7"
                        />
                      </svg>
                    </div>
                  </motion.div>
                </Link>
              ))}
            </div>
          ) : (
            <div className="bg-surface-card rounded-xl p-8 border border-border-subtle text-center">
              <Camera className="w-12 h-12 text-text-secondary mx-auto mb-3" />
              <p className="text-text-secondary">No scans yet. Start by scanning your crops!</p>
              <Link
                href="/scan"
                className="inline-block mt-4 px-6 py-2 bg-primary text-white rounded-full font-semibold hover:bg-primary-600 transition-colors"
              >
                Scan Now
              </Link>
            </div>
          )}
        </motion.div>
      </div>
    </Layout>
  )
}
