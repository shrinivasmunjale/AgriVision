'use client'

import { useAuth } from '@/contexts/AuthContext'
import { useRouter } from 'next/navigation'
import { useEffect, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { predictionsAPI } from '@/lib/api'
import Layout from '@/components/Layout'
import { Search } from 'lucide-react'
import { motion } from 'framer-motion'
import Link from 'next/link'

export default function HistoryPage() {
  const { user, loading, getAccessToken } = useAuth()
  const router = useRouter()
  const [searchTerm, setSearchTerm] = useState('')

  useEffect(() => {
    if (!loading && !user) {
      router.push('/auth/login')
    }
  }, [user, loading, router])

  const { data: predictions, isLoading } = useQuery({
    queryKey: ['all-predictions'],
    queryFn: async () => {
      const token = await getAccessToken()
      const response = await predictionsAPI.getAll({ limit: 100 }, token)
      return response.data
    },
    enabled: !!user,
  })

  if (loading || !user) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="w-16 h-16 border-4 border-primary-400 border-t-transparent rounded-full animate-spin"></div>
      </div>
    )
  }

  const filteredPredictions = predictions?.filter((p) =>
    p.disease_name?.toLowerCase().includes(searchTerm.toLowerCase())
  )

  return (
    <Layout>
      <div className="p-4 lg:p-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <h1 className="text-3xl font-bold text-text-primary mb-2">
            Prediction History
          </h1>
          <p className="text-text-secondary mb-6">
            Review your past crop health analyses
          </p>

          <div className="mb-6">
            <div className="relative">
              <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-text-secondary" />
              <input
                type="text"
                placeholder="Search by disease name..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-12 pr-4 py-3 bg-surface-card border border-border-subtle rounded-xl text-text-primary focus:outline-none focus:ring-2 focus:ring-primary-400"
              />
            </div>
          </div>

          {isLoading ? (
            <div className="text-center py-12">
              <div className="w-12 h-12 border-4 border-primary-400 border-t-transparent rounded-full animate-spin mx-auto"></div>
              <p className="mt-4 text-text-secondary">Loading predictions...</p>
            </div>
          ) : filteredPredictions && filteredPredictions.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {filteredPredictions.map((prediction, index) => (
                <Link
                  key={prediction.id}
                  href={`/history/${prediction.id}`}
                  className="block"
                >
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.05 }}
                    className="bg-surface-card rounded-xl overflow-hidden border border-border-subtle hover:border-primary-400 transition-colors group"
                  >
                    <div className="aspect-video bg-surface-base relative overflow-hidden">
                      <img
                        src={prediction.image_url}
                        alt="Leaf scan"
                        className="w-full h-full object-cover group-hover:scale-105 transition-transform"
                      />
                    </div>
                    <div className="p-4">
                      <div className="flex items-center justify-between mb-2">
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
                          {(prediction.confidence_score * 100).toFixed(1)}%
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
                  </motion.div>
                </Link>
              ))}
            </div>
          ) : (
            <div className="text-center py-12">
              <p className="text-text-secondary">No predictions found</p>
            </div>
          )}
        </motion.div>
      </div>
    </Layout>
  )
}
