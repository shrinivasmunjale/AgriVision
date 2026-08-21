'use client'

import { useAuth } from '@/contexts/AuthContext'
import { useRouter } from 'next/navigation'
import { useEffect, useState } from 'react'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { predictionsAPI } from '@/lib/api'
import Layout from '@/components/Layout'
import { Search, Trash2, AlertTriangle, X } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import Link from 'next/link'

export default function HistoryPage() {
  const { user, loading, getAccessToken } = useAuth()
  const router = useRouter()
  const queryClient = useQueryClient()
  const [searchTerm, setSearchTerm] = useState('')
  
  // Modal states
  const [showClearModal, setShowClearModal] = useState(false)
  const [itemToDelete, setItemToDelete] = useState(null) // null or prediction object
  const [isDeleting, setIsDeleting] = useState(false)

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

  const handleClearAllHistory = async () => {
    try {
      setIsDeleting(true)
      const token = await getAccessToken()
      await predictionsAPI.clearAll(token)
      await queryClient.invalidateQueries({ queryKey: ['all-predictions'] })
      setShowClearModal(false)
    } catch (error) {
      console.error('Failed to clear prediction history:', error)
    } finally {
      setIsDeleting(false)
    }
  }

  const handleDeleteItem = async () => {
    if (!itemToDelete) return
    try {
      setIsDeleting(true)
      const token = await getAccessToken()
      await predictionsAPI.deleteById(itemToDelete.id, token)
      await queryClient.invalidateQueries({ queryKey: ['all-predictions'] })
      setItemToDelete(null)
    } catch (error) {
      console.error('Failed to delete prediction item:', error)
    } finally {
      setIsDeleting(false)
    }
  }

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
      <div className="p-4 lg:p-8 relative">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          {/* Header with Clear History Button */}
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
            <div>
              <h1 className="text-3xl font-bold text-text-primary mb-1">
                Prediction History
              </h1>
              <p className="text-text-secondary text-sm">
                Review and manage your past crop health analyses
              </p>
            </div>

            {predictions && predictions.length > 0 && (
              <button
                onClick={() => setShowClearModal(true)}
                className="self-start sm:self-auto flex items-center gap-2 px-4 py-2.5 bg-red-500/10 hover:bg-red-500/20 text-red-400 border border-red-500/30 rounded-xl text-sm font-medium transition-all shadow-sm active:scale-95"
              >
                <Trash2 className="w-4 h-4" />
                Clear All History
              </button>
            )}
          </div>

          {/* Search bar */}
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

          {/* Prediction list / grid */}
          {isLoading ? (
            <div className="text-center py-12">
              <div className="w-12 h-12 border-4 border-primary-400 border-t-transparent rounded-full animate-spin mx-auto"></div>
              <p className="mt-4 text-text-secondary">Loading predictions...</p>
            </div>
          ) : filteredPredictions && filteredPredictions.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {filteredPredictions.map((prediction, index) => (
                <div key={prediction.id} className="relative group">
                  <Link
                    href={`/history/${prediction.id}`}
                    className="block"
                  >
                    <motion.div
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: index * 0.05 }}
                      className="bg-surface-card rounded-xl overflow-hidden border border-border-subtle hover:border-primary-400 transition-colors"
                    >
                      <div className="aspect-video bg-surface-base relative overflow-hidden">
                        <img
                          src={prediction.image_url}
                          alt="Leaf scan"
                          className="w-full h-full object-cover group-hover:scale-105 transition-transform"
                          onError={(e) => {
                            e.target.src = '/placeholder-leaf.png'
                          }}
                        />
                      </div>
                      <div className="p-4 pr-12">
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

                  {/* Single item delete button */}
                  <button
                    onClick={(e) => {
                      e.preventDefault()
                      e.stopPropagation()
                      setItemToDelete(prediction)
                    }}
                    title="Delete record"
                    className="absolute bottom-3 right-3 p-2 text-text-secondary hover:text-red-400 bg-surface-base/80 hover:bg-surface-base border border-border-subtle rounded-lg opacity-80 hover:opacity-100 transition-all"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-12 bg-surface-card border border-border-subtle rounded-2xl p-8">
              <p className="text-text-secondary text-lg">No predictions found</p>
              <p className="text-text-secondary text-sm mt-1">
                {searchTerm ? 'Try a different search query' : 'Your scan history is empty'}
              </p>
            </div>
          )}
        </motion.div>

        {/* Clear All Confirmation Modal */}
        <AnimatePresence>
          {showClearModal && (
            <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
              <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.95 }}
                className="bg-surface-card border border-border-subtle rounded-2xl max-w-md w-full p-6 shadow-2xl relative"
              >
                <button
                  onClick={() => setShowClearModal(false)}
                  className="absolute top-4 right-4 text-text-secondary hover:text-text-primary"
                >
                  <X className="w-5 h-5" />
                </button>

                <div className="flex items-center gap-3 text-red-400 mb-4">
                  <div className="p-3 bg-red-500/10 rounded-xl">
                    <AlertTriangle className="w-6 h-6" />
                  </div>
                  <h3 className="text-xl font-bold text-text-primary">Clear All History?</h3>
                </div>

                <p className="text-text-secondary text-sm mb-6">
                  Are you sure you want to permanently delete all prediction records and reports? This action cannot be undone.
                </p>

                <div className="flex justify-end gap-3">
                  <button
                    disabled={isDeleting}
                    onClick={() => setShowClearModal(false)}
                    className="px-4 py-2 bg-surface-base border border-border-subtle hover:bg-surface-card rounded-xl text-sm font-medium text-text-primary transition-colors"
                  >
                    Cancel
                  </button>
                  <button
                    disabled={isDeleting}
                    onClick={handleClearAllHistory}
                    className="flex items-center gap-2 px-5 py-2 bg-red-500 hover:bg-red-600 text-white rounded-xl text-sm font-medium transition-colors disabled:opacity-50"
                  >
                    {isDeleting ? (
                      <>
                        <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                        Clearing...
                      </>
                    ) : (
                      <>
                        <Trash2 className="w-4 h-4" />
                        Confirm Clear
                      </>
                    )}
                  </button>
                </div>
              </motion.div>
            </div>
          )}
        </AnimatePresence>

        {/* Delete Single Item Confirmation Modal */}
        <AnimatePresence>
          {itemToDelete && (
            <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
              <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.95 }}
                className="bg-surface-card border border-border-subtle rounded-2xl max-w-md w-full p-6 shadow-2xl relative"
              >
                <button
                  onClick={() => setItemToDelete(null)}
                  className="absolute top-4 right-4 text-text-secondary hover:text-text-primary"
                >
                  <X className="w-5 h-5" />
                </button>

                <div className="flex items-center gap-3 text-red-400 mb-4">
                  <div className="p-3 bg-red-500/10 rounded-xl">
                    <Trash2 className="w-6 h-6" />
                  </div>
                  <h3 className="text-xl font-bold text-text-primary">Delete Record?</h3>
                </div>

                <p className="text-text-secondary text-sm mb-6">
                  Are you sure you want to delete the record for <strong className="text-text-primary">{itemToDelete.disease_name || 'Prediction'}</strong>?
                </p>

                <div className="flex justify-end gap-3">
                  <button
                    disabled={isDeleting}
                    onClick={() => setItemToDelete(null)}
                    className="px-4 py-2 bg-surface-base border border-border-subtle hover:bg-surface-card rounded-xl text-sm font-medium text-text-primary transition-colors"
                  >
                    Cancel
                  </button>
                  <button
                    disabled={isDeleting}
                    onClick={handleDeleteItem}
                    className="flex items-center gap-2 px-5 py-2 bg-red-500 hover:bg-red-600 text-white rounded-xl text-sm font-medium transition-colors disabled:opacity-50"
                  >
                    {isDeleting ? (
                      <>
                        <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                        Deleting...
                      </>
                    ) : (
                      'Delete'
                    )}
                  </button>
                </div>
              </motion.div>
            </div>
          )}
        </AnimatePresence>
      </div>
    </Layout>
  )
}
