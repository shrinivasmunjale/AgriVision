'use client'

import { useAuth } from '@/contexts/AuthContext'
import { useRouter } from 'next/navigation'
import { useEffect, useState, useMemo } from 'react'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { predictionsAPI } from '@/lib/api'
import Layout from '@/components/Layout'
import { Search, Layers, LayoutGrid, AlertCircle, ChevronDown, ChevronUp, Trash2, ArrowRight } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import { useI18n } from '@/contexts/I18nContext'
import Link from 'next/link'

export default function HistoryPage() {
  const { user, loading, getAccessToken, profile } = useAuth()
  const router = useRouter()
  const queryClient = useQueryClient()
  const { t } = useI18n()
  const [searchTerm, setSearchTerm] = useState('')
  const [viewTab, setViewTab] = useState('all') // 'all' | 'grouped'
  const [collapsedGroups, setCollapsedGroups] = useState({})
  const [itemToDelete, setItemToDelete] = useState(null)
  const [deleting, setDeleting] = useState(false)
  const [deleteError, setDeleteError] = useState('')

  useEffect(() => {
    if (!loading) {
      if (!user) router.push('/auth/login')
      else if (profile?.role === 'admin') router.push('/admin')
    }
  }, [user, loading, profile, router])

  const { data: predictions, isLoading } = useQuery({
    queryKey: ['all-predictions'],
    queryFn: async () => {
      const token = await getAccessToken()
      const response = await predictionsAPI.getAll({ limit: 100 }, token)
      return response.data
    },
    enabled: !!user && profile?.role !== 'admin',
  })

  // Group predictions by disease
  const diseaseGroups = useMemo(() => {
    if (!predictions) return []
    const groups = {}
    predictions.forEach((pred) => {
      const diseaseKey = pred.disease_name || 'Unknown'
      if (!groups[diseaseKey]) {
        groups[diseaseKey] = {
          name: diseaseKey,
          items: [],
          avgConfidence: 0,
        }
      }
      groups[diseaseKey].items.push(pred)
    })

    return Object.values(groups).map((group) => {
      const sumConf = group.items.reduce((acc, curr) => acc + curr.confidence_score, 0)
      group.avgConfidence = group.items.length > 0 ? sumConf / group.items.length : 0
      return group
    })
  }, [predictions])

  const toggleGroupCollapse = (groupName) => {
    setCollapsedGroups((prev) => ({
      ...prev,
      [groupName]: !prev[groupName],
    }))
  }

  const handleDelete = async () => {
    if (!itemToDelete) return
    setDeleting(true)
    setDeleteError('')
    try {
      const token = await getAccessToken()
      await predictionsAPI.delete(itemToDelete.id, token)
      await queryClient.invalidateQueries({ queryKey: ['all-predictions'] })
      await queryClient.invalidateQueries({ queryKey: ['predictions'] })
      setItemToDelete(null)
    } catch (err) {
      console.error('Failed to delete prediction:', err)
      setDeleteError(err.response?.data?.detail || 'Failed to delete scan')
    } finally {
      setDeleting(false)
    }
  }

  if (loading || !user) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="w-16 h-16 border-4 border-primary-400 border-t-transparent rounded-full animate-spin"></div>
      </div>
    )
  }

  if (profile?.role === 'admin') {
    return null
  }

  const filteredPredictions = predictions?.filter((p) =>
    p.disease_name?.toLowerCase().includes(searchTerm.toLowerCase())
  )

  const filteredGroups = diseaseGroups
    .map((grp) => ({
      ...grp,
      items: grp.items.filter((p) =>
        p.disease_name?.toLowerCase().includes(searchTerm.toLowerCase())
      ),
    }))
    .filter((grp) => grp.items.length > 0)

  return (
    <Layout>
      <div className="p-4 lg:p-8">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-4">
            <div>
              <h1 className="text-3xl font-bold text-text-primary mb-1">{t('history.title')}</h1>
              <p className="text-text-secondary">{t('history.subtitle')}</p>
            </div>

            {/* View Mode Toggle: All vs Grouped by Disease */}
            <div className="flex bg-surface-card p-1 rounded-xl border border-border-subtle self-start sm:self-auto">
              <button
                onClick={() => setViewTab('all')}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors ${
                  viewTab === 'all'
                    ? 'bg-primary-400 text-white shadow'
                    : 'text-text-secondary hover:text-text-primary'
                }`}
              >
                <LayoutGrid className="w-3.5 h-3.5" />
                {t('history.allScans')}
              </button>
              <button
                onClick={() => setViewTab('grouped')}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors ${
                  viewTab === 'grouped'
                    ? 'bg-primary-400 text-white shadow'
                    : 'text-text-secondary hover:text-text-primary'
                }`}
              >
                <Layers className="w-3.5 h-3.5" />
                {t('history.grouped')}
              </button>
            </div>
          </div>

          <div className="mb-6">
            <div className="relative">
              <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-text-secondary" />
              <input
                type="text"
                placeholder={t('history.search')}
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
          ) : viewTab === 'grouped' ? (
            /* GROUPED BY DISEASE VIEW */
            filteredGroups && filteredGroups.length > 0 ? (
              <div className="space-y-6">
                {filteredGroups.map((group) => {
                  const isHealthy = group.name === 'Healthy'
                  const isCollapsed = !collapsedGroups[group.name]

                  return (
                    <div
                      key={group.name}
                      className="bg-surface-card rounded-2xl border border-border-subtle overflow-hidden"
                    >
                      {/* Group Header Banner */}
                      <button
                        onClick={() => toggleGroupCollapse(group.name)}
                        className="w-full flex items-center justify-between p-5 bg-surface-base/50 hover:bg-surface-base transition-colors border-b border-border-subtle text-left"
                      >
                        <div className="flex items-center gap-3">
                          <span
                            className={`w-3.5 h-3.5 rounded-full ${
                              isHealthy ? 'bg-status-successText' : 'bg-status-dangerText'
                            }`}
                          ></span>
                          <div>
                            <h3 className="text-lg font-bold text-text-primary flex items-center gap-2">
                              {group.name}
                              <span className="text-xs px-2.5 py-0.5 rounded-full bg-primary-400/20 text-primary-400 font-semibold">
                                {group.items.length} {group.items.length === 1 ? 'Leaf' : 'Leaves'}
                              </span>
                            </h3>
                            <p className="text-xs text-text-secondary mt-0.5">
                              Average Confidence:{' '}
                              <span className="font-semibold text-text-primary">
                                {(group.avgConfidence * 100).toFixed(1)}%
                              </span>
                            </p>
                          </div>
                        </div>

                        <div className="flex items-center gap-2 text-text-secondary">
                          <span className="text-xs hidden sm:inline">
                            {isCollapsed ? 'Show Items' : 'Hide Items'}
                          </span>
                          {isCollapsed ? (
                            <ChevronDown className="w-5 h-5" />
                          ) : (
                            <ChevronUp className="w-5 h-5" />
                          )}
                        </div>
                      </button>

                      {/* Group Items Grid */}
                      <AnimatePresence initial={false}>
                        {!isCollapsed && (
                          <motion.div
                            initial={{ height: 0, opacity: 0 }}
                            animate={{ height: 'auto', opacity: 1 }}
                            exit={{ height: 0, opacity: 0 }}
                            transition={{ duration: 0.2 }}
                            className="p-5"
                          >
                            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                              {group.items.map((prediction) => (
                                <PredictionCard
                                  key={prediction.id}
                                  prediction={prediction}
                                  onDelete={() => setItemToDelete(prediction)}
                                  t={t}
                                />
                              ))}
                            </div>
                          </motion.div>
                        )}
                      </AnimatePresence>
                    </div>
                  )
                })}
              </div>
            ) : (
              <div className="text-center py-12">
                <p className="text-text-secondary">{t('history.noPredictions')}</p>
              </div>
            )
          ) : /* ALL SCANS STANDARD GRID VIEW */
          filteredPredictions && filteredPredictions.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {filteredPredictions.map((prediction, index) => (
                <PredictionCard
                  key={prediction.id}
                  prediction={prediction}
                  delay={index * 0.03}
                  onDelete={() => setItemToDelete(prediction)}
                  t={t}
                />
              ))}
            </div>
          ) : (
            <div className="text-center py-12">
              <p className="text-text-secondary">{t('history.noPredictions')}</p>
            </div>
          )}
        </motion.div>

        {/* Delete Confirmation Modal */}
        <AnimatePresence>
          {itemToDelete && (
            <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
              <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.95 }}
                className="bg-surface-card border border-border-subtle rounded-2xl max-w-md w-full p-6 shadow-2xl"
              >
                <div className="flex items-center gap-3 mb-4 text-status-dangerText">
                  <div className="w-10 h-10 rounded-full bg-status-dangerBg flex items-center justify-center flex-shrink-0">
                    <Trash2 className="w-5 h-5" />
                  </div>
                  <div>
                    <h3 className="text-lg font-bold text-text-primary">
                      {t('history.delete')} {itemToDelete.disease_name || 'Scan'}
                    </h3>
                    <p className="text-xs text-text-secondary">
                      This action cannot be undone.
                    </p>
                  </div>
                </div>

                <p className="text-sm text-text-secondary mb-6">
                  {t('history.deleteConfirm')}
                </p>

                {deleteError && (
                  <p className="text-xs text-status-dangerText mb-4 bg-status-dangerBg p-2.5 rounded-lg">
                    {deleteError}
                  </p>
                )}

                <div className="flex items-center justify-end gap-3">
                  <button
                    onClick={() => setItemToDelete(null)}
                    disabled={deleting}
                    className="px-4 py-2 text-sm font-medium text-text-secondary hover:text-text-primary rounded-xl transition-colors"
                  >
                    {t('history.cancel')}
                  </button>
                  <button
                    onClick={handleDelete}
                    disabled={deleting}
                    className="px-5 py-2 text-sm font-semibold bg-red-600 text-white rounded-xl hover:bg-red-700 transition-colors disabled:opacity-50 flex items-center gap-2 shadow-lg shadow-red-600/20"
                  >
                    {deleting ? 'Deleting...' : t('history.delete')}
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

function PredictionCard({ prediction, delay = 0, onDelete, t }) {
  const isHealthy = prediction.disease_name === 'Healthy'
  const displayImage = prediction.annotated_image_url || prediction.image_url

  return (
    <motion.div
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay }}
      className="bg-surface-base rounded-2xl overflow-hidden border border-border-subtle hover:border-primary-400/50 transition-all group flex flex-col justify-between shadow-sm"
    >
      <Link href={`/history/${prediction.id}`} className="block relative aspect-video bg-surface-card overflow-hidden">
        <img
          src={displayImage}
          alt="Leaf scan"
          className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
        />
        {prediction.annotated_image_url && (
          <div className="absolute top-2 right-2 bg-black/75 backdrop-blur-sm px-2 py-0.5 rounded-full text-[10px] text-white font-semibold flex items-center gap-1 border border-white/20">
            <span className="w-1.5 h-1.5 rounded-full bg-red-400 animate-pulse"></span>
            YOLO BBox
          </div>
        )}
      </Link>

      <div className="p-4 flex-1 flex flex-col justify-between">
        <div>
          <div className="flex items-center justify-between mb-2">
            <span
              className={`px-3 py-1 rounded-full text-xs font-bold ${
                isHealthy
                  ? 'bg-status-successBg text-status-successText'
                  : 'bg-status-dangerBg text-status-dangerText'
              }`}
            >
              {prediction.disease_name || 'Unknown'}
            </span>
            <span className="text-text-primary text-sm font-black">
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

        <div className="flex items-center justify-between gap-2 mt-4 pt-3 border-t border-border-subtle">
          <Link
            href={`/history/${prediction.id}`}
            className="text-xs font-semibold text-primary-400 hover:text-primary-300 flex items-center gap-1 transition-colors"
          >
            {t('history.viewDetails')} <ArrowRight className="w-3 h-3" />
          </Link>
          <button
            onClick={(e) => {
              e.preventDefault()
              e.stopPropagation()
              onDelete()
            }}
            title={t('history.delete')}
            className="p-1.5 text-text-secondary hover:text-status-dangerText hover:bg-status-dangerBg rounded-lg transition-colors"
          >
            <Trash2 className="w-4 h-4" />
          </button>
        </div>
      </div>
    </motion.div>
  )
}
