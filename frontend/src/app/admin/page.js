'use client'

import { useAuth } from '@/contexts/AuthContext'
import { useRouter } from 'next/navigation'
import { useEffect, useState } from 'react'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { adminAPI } from '@/lib/api'
import Layout from '@/components/Layout'
import {
  Users,
  Activity,
  TrendingUp,
  Database,
  Search,
  Trash2,
  ExternalLink,
  MessageSquare,
  History,
  BarChart3,
  Calendar,
  User as UserIcon,
  Mail,
  CheckCircle,
  Clock,
  Eye,
  X,
  Target
} from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import { useI18n } from '@/contexts/I18nContext'
import Link from 'next/link'

export default function AdminPage() {
  const { user, loading, getAccessToken, profile } = useAuth()
  const router = useRouter()
  const queryClient = useQueryClient()
  const { t } = useI18n()

  const [activeTab, setActiveTab] = useState('overview') // 'overview' | 'predictions' | 'contacts'
  const [predictionSearch, setPredictionSearch] = useState('')
  const [contactSearch, setContactSearch] = useState('')

  // Modals
  const [selectedPrediction, setSelectedPrediction] = useState(null)
  const [selectedContact, setSelectedContact] = useState(null)
  const [deleteTarget, setDeleteTarget] = useState(null) // { type: 'prediction' | 'contact', item: object }
  const [deleting, setDeleting] = useState(false)
  const [deleteError, setDeleteError] = useState('')

  useEffect(() => {
    if (!loading && !user) {
      router.push('/auth/login')
    } else if (!loading && profile && profile.role !== 'admin') {
      router.push('/dashboard')
    }
  }, [user, loading, profile, router])

  // Fetch Analytics
  const { data: analytics, isLoading: analyticsLoading } = useQuery({
    queryKey: ['admin-analytics'],
    queryFn: async () => {
      const token = await getAccessToken()
      const response = await adminAPI.getAnalytics(token)
      return response.data
    },
    enabled: !!user && profile?.role === 'admin',
  })

  // Fetch All User Predictions
  const { data: userPredictionsData, isLoading: predictionsLoading } = useQuery({
    queryKey: ['admin-predictions', predictionSearch],
    queryFn: async () => {
      const token = await getAccessToken()
      const response = await adminAPI.getPredictions(
        { search: predictionSearch, limit: 100 },
        token
      )
      return response.data
    },
    enabled: !!user && profile?.role === 'admin' && activeTab === 'predictions',
  })

  // Fetch Contact Messages
  const { data: contactsData, isLoading: contactsLoading } = useQuery({
    queryKey: ['admin-contacts', contactSearch],
    queryFn: async () => {
      const token = await getAccessToken()
      const response = await adminAPI.getContacts(
        { search: contactSearch, limit: 100 },
        token
      )
      return response.data
    },
    enabled: !!user && profile?.role === 'admin' && activeTab === 'contacts',
  })

  const handleDeleteConfirm = async () => {
    if (!deleteTarget) return
    setDeleting(true)
    setDeleteError('')

    try {
      const token = await getAccessToken()
      if (deleteTarget.type === 'prediction') {
        await adminAPI.deletePrediction(deleteTarget.item.id, token)
        await queryClient.invalidateQueries({ queryKey: ['admin-predictions'] })
        await queryClient.invalidateQueries({ queryKey: ['admin-analytics'] })
      } else if (deleteTarget.type === 'contact') {
        await adminAPI.deleteContact(deleteTarget.item.id, token)
        await queryClient.invalidateQueries({ queryKey: ['admin-contacts'] })
      }
      setDeleteTarget(null)
    } catch (err) {
      console.error('Delete failed:', err)
      setDeleteError(err.response?.data?.detail || 'Failed to delete record')
    } finally {
      setDeleting(false)
    }
  }

  if (loading || !user || !profile || profile.role !== 'admin') {
    return (
      <Layout>
        <div className="flex items-center justify-center min-h-screen">
          <div className="w-16 h-16 border-4 border-primary-400 border-t-transparent rounded-full animate-spin"></div>
        </div>
      </Layout>
    )
  }

  const predictionsList = userPredictionsData?.items || []
  const contactsList = contactsData?.items || []

  return (
    <Layout>
      <div className="p-4 lg:p-8">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
          {/* Header */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
            <div>
              <h1 className="text-3xl font-bold text-text-primary mb-1">
                {t('admin.title')}
              </h1>
              <p className="text-text-secondary">
                {t('admin.subtitle')}
              </p>
            </div>

            {/* Navigation Tabs */}
            <div className="flex bg-surface-card p-1 rounded-2xl border border-border-subtle overflow-x-auto">
              <button
                onClick={() => setActiveTab('overview')}
                className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold transition-colors whitespace-nowrap ${
                  activeTab === 'overview'
                    ? 'bg-primary-400 text-white shadow'
                    : 'text-text-secondary hover:text-text-primary'
                }`}
              >
                <BarChart3 className="w-4 h-4" />
                {t('admin.tabOverview')}
              </button>
              <button
                onClick={() => setActiveTab('predictions')}
                className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold transition-colors whitespace-nowrap ${
                  activeTab === 'predictions'
                    ? 'bg-primary-400 text-white shadow'
                    : 'text-text-secondary hover:text-text-primary'
                }`}
              >
                <History className="w-4 h-4" />
                {t('admin.tabPredictions')}
              </button>
              <button
                onClick={() => setActiveTab('contacts')}
                className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold transition-colors whitespace-nowrap ${
                  activeTab === 'contacts'
                    ? 'bg-primary-400 text-white shadow'
                    : 'text-text-secondary hover:text-text-primary'
                }`}
              >
                <MessageSquare className="w-4 h-4" />
                {t('admin.tabContacts')}
              </button>
            </div>
          </div>

          {/* TAB 1: OVERVIEW & ANALYTICS */}
          {activeTab === 'overview' && (
            <div>
              {analyticsLoading ? (
                <div className="text-center py-16">
                  <div className="w-12 h-12 border-4 border-primary-400 border-t-transparent rounded-full animate-spin mx-auto"></div>
                </div>
              ) : analytics ? (
                <>
                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
                    <motion.div
                      initial={{ opacity: 0, y: 15 }}
                      animate={{ opacity: 1, y: 0 }}
                      className="bg-surface-card rounded-2xl p-6 border border-border-subtle shadow-sm"
                    >
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="text-text-secondary text-xs uppercase tracking-wider font-semibold mb-1">
                            Total Users
                          </p>
                          <p className="text-3xl font-black text-text-primary">
                            {analytics.total_users}
                          </p>
                        </div>
                        <div className="w-12 h-12 bg-primary-400/20 rounded-2xl flex items-center justify-center">
                          <Users className="w-6 h-6 text-primary-400" />
                        </div>
                      </div>
                    </motion.div>

                    <motion.div
                      initial={{ opacity: 0, y: 15 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: 0.1 }}
                      className="bg-surface-card rounded-2xl p-6 border border-border-subtle shadow-sm"
                    >
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="text-text-secondary text-xs uppercase tracking-wider font-semibold mb-1">
                            Total Scans
                          </p>
                          <p className="text-3xl font-black text-text-primary">
                            {analytics.total_predictions}
                          </p>
                        </div>
                        <div className="w-12 h-12 bg-primary-400/20 rounded-2xl flex items-center justify-center">
                          <Activity className="w-6 h-6 text-primary-400" />
                        </div>
                      </div>
                    </motion.div>

                    <motion.div
                      initial={{ opacity: 0, y: 15 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: 0.2 }}
                      className="bg-surface-card rounded-2xl p-6 border border-border-subtle shadow-sm"
                    >
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="text-text-secondary text-xs uppercase tracking-wider font-semibold mb-1">
                            Avg Confidence
                          </p>
                          <p className="text-3xl font-black text-text-primary">
                            {(analytics.average_confidence * 100).toFixed(0)}%
                          </p>
                        </div>
                        <div className="w-12 h-12 bg-primary-400/20 rounded-2xl flex items-center justify-center">
                          <TrendingUp className="w-6 h-6 text-primary-400" />
                        </div>
                      </div>
                    </motion.div>

                    <motion.div
                      initial={{ opacity: 0, y: 15 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: 0.3 }}
                      className="bg-surface-card rounded-2xl p-6 border border-border-subtle shadow-sm"
                    >
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="text-text-secondary text-xs uppercase tracking-wider font-semibold mb-1">
                            Diseases
                          </p>
                          <p className="text-3xl font-black text-text-primary">
                            {analytics.disease_distribution?.length || 0}
                          </p>
                        </div>
                        <div className="w-12 h-12 bg-primary-400/20 rounded-2xl flex items-center justify-center">
                          <Database className="w-6 h-6 text-primary-400" />
                        </div>
                      </div>
                    </motion.div>
                  </div>

                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    {/* Disease Distribution */}
                    <div className="bg-surface-card rounded-2xl p-6 border border-border-subtle shadow-sm">
                      <h2 className="text-lg font-bold text-text-primary mb-4">
                        Disease Distribution
                      </h2>
                      <div className="space-y-4">
                        {analytics.disease_distribution?.map((item, index) => {
                          const total = analytics.total_predictions
                          const percentage = total > 0 ? ((item.count / total) * 100).toFixed(1) : 0
                          return (
                            <div key={index}>
                              <div className="flex items-center justify-between mb-1.5 text-xs">
                                <span className="font-semibold text-text-primary">{item.disease}</span>
                                <span className="text-text-secondary">
                                  {item.count} ({percentage}%)
                                </span>
                              </div>
                              <div className="w-full bg-surface-base rounded-full h-2 overflow-hidden">
                                <div
                                  className="bg-primary-400 h-2 rounded-full transition-all duration-500"
                                  style={{ width: `${percentage}%` }}
                                />
                              </div>
                            </div>
                          )
                        })}
                      </div>
                    </div>

                    {/* Recent Audits */}
                    <div className="bg-surface-card rounded-2xl p-6 border border-border-subtle shadow-sm">
                      <h2 className="text-lg font-bold text-text-primary mb-4">
                        Recent Admin Audit Logs
                      </h2>
                      {analytics.recent_audits && analytics.recent_audits.length > 0 ? (
                        <div className="space-y-3">
                          {analytics.recent_audits.map((audit, index) => (
                            <div
                              key={index}
                              className="flex items-center justify-between p-3 bg-surface-base rounded-xl border border-border-subtle text-xs"
                            >
                              <div>
                                <p className="text-text-primary font-semibold">
                                  <span className="text-primary-400 font-bold uppercase">{audit.action}</span> {audit.entity}
                                </p>
                                <p className="text-text-secondary text-[11px] mt-0.5">
                                  {new Date(audit.timestamp).toLocaleString()}
                                </p>
                              </div>
                              <span className="text-text-secondary font-mono text-[11px]">
                                ID: {audit.entity_id?.slice(0, 8)}...
                              </span>
                            </div>
                          ))}
                        </div>
                      ) : (
                        <p className="text-text-secondary text-center py-8 text-sm">
                          No recent activity recorded
                        </p>
                      )}
                    </div>
                  </div>
                </>
              ) : null}
            </div>
          )}

          {/* TAB 2: USER PREDICTIONS HISTORY */}
          {activeTab === 'predictions' && (
            <div className="space-y-4">
              {/* Search Bar */}
              <div className="relative">
                <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-text-secondary" />
                <input
                  type="text"
                  placeholder={t('admin.searchPredictions')}
                  value={predictionSearch}
                  onChange={(e) => setPredictionSearch(e.target.value)}
                  className="w-full pl-12 pr-4 py-3 bg-surface-card border border-border-subtle rounded-xl text-text-primary focus:outline-none focus:ring-2 focus:ring-primary-400 text-sm"
                />
              </div>

              {predictionsLoading ? (
                <div className="text-center py-16">
                  <div className="w-12 h-12 border-4 border-primary-400 border-t-transparent rounded-full animate-spin mx-auto"></div>
                </div>
              ) : predictionsList.length > 0 ? (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {predictionsList.map((pred) => {
                    const isHealthy = pred.disease_name === 'Healthy'
                    const displayImage = pred.annotated_image_url || pred.image_url

                    return (
                      <div
                        key={pred.id}
                        className="bg-surface-card rounded-2xl overflow-hidden border border-border-subtle shadow-sm flex flex-col justify-between"
                      >
                        {/* Leaf Preview Image */}
                        <div
                          onClick={() => setSelectedPrediction(pred)}
                          className="cursor-pointer relative aspect-video bg-surface-base overflow-hidden group"
                        >
                          <img
                            src={displayImage}
                            alt="Leaf scan"
                            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                          />
                          {pred.annotated_image_url && (
                            <div className="absolute top-2 right-2 bg-black/80 backdrop-blur-sm px-2.5 py-1 rounded-full text-[10px] text-white font-semibold flex items-center gap-1 border border-white/20">
                              <span className="w-1.5 h-1.5 rounded-full bg-red-400 animate-pulse"></span>
                              YOLO BBox
                            </div>
                          )}
                          <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center text-white text-xs font-semibold gap-1.5">
                            <Eye className="w-4 h-4" /> Quick Preview
                          </div>
                        </div>

                        {/* Content */}
                        <div className="p-4 flex-1 flex flex-col justify-between">
                          <div>
                            {/* User details */}
                            <div className="flex items-center gap-2 mb-3 pb-2.5 border-b border-border-subtle">
                              <div className="w-8 h-8 rounded-full bg-primary-400/20 text-primary-400 font-bold text-xs flex items-center justify-center flex-shrink-0">
                                {pred.user_name?.charAt(0)?.toUpperCase() || 'U'}
                              </div>
                              <div className="overflow-hidden">
                                <p className="text-xs font-bold text-text-primary truncate">
                                  {pred.user_name}
                                </p>
                                <p className="text-[11px] text-text-secondary truncate">
                                  {pred.user_email}
                                </p>
                              </div>
                            </div>

                            {/* Diagnosis */}
                            <div className="flex items-center justify-between mb-2">
                              <span
                                className={`px-2.5 py-1 rounded-lg text-xs font-bold ${
                                  isHealthy
                                    ? 'bg-status-successBg text-status-successText'
                                    : 'bg-status-dangerBg text-status-dangerText'
                                }`}
                              >
                                {pred.disease_name}
                              </span>
                              <span className="text-xs font-black text-text-primary">
                                {(pred.confidence_score * 100).toFixed(1)}%
                              </span>
                            </div>

                            <p className="text-[11px] text-text-secondary flex items-center gap-1">
                              <Calendar className="w-3 h-3" />
                              {new Date(pred.created_at).toLocaleString()}
                            </p>
                          </div>

                          {/* Action Buttons */}
                          <div className="flex items-center justify-between gap-2 mt-4 pt-3 border-t border-border-subtle">
                            <Link
                              href={`/history/${pred.id}`}
                              className="text-xs font-semibold text-primary-400 hover:text-primary-300 flex items-center gap-1"
                            >
                              Full Report <ExternalLink className="w-3 h-3" />
                            </Link>

                            <button
                              onClick={() => setDeleteTarget({ type: 'prediction', item: pred })}
                              title={t('admin.delete')}
                              className="p-1.5 text-text-secondary hover:text-status-dangerText hover:bg-status-dangerBg rounded-lg transition-colors"
                            >
                              <Trash2 className="w-4 h-4" />
                            </button>
                          </div>
                        </div>
                      </div>
                    )
                  })}
                </div>
              ) : (
                <div className="text-center py-16 bg-surface-card rounded-2xl border border-border-subtle">
                  <p className="text-text-secondary text-sm">{t('admin.noPredictions')}</p>
                </div>
              )}
            </div>
          )}

          {/* TAB 3: CONTACT INQUIRIES */}
          {activeTab === 'contacts' && (
            <div className="space-y-4">
              {/* Search Bar */}
              <div className="relative">
                <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-text-secondary" />
                <input
                  type="text"
                  placeholder={t('admin.searchContacts')}
                  value={contactSearch}
                  onChange={(e) => setContactSearch(e.target.value)}
                  className="w-full pl-12 pr-4 py-3 bg-surface-card border border-border-subtle rounded-xl text-text-primary focus:outline-none focus:ring-2 focus:ring-primary-400 text-sm"
                />
              </div>

              {contactsLoading ? (
                <div className="text-center py-16">
                  <div className="w-12 h-12 border-4 border-primary-400 border-t-transparent rounded-full animate-spin mx-auto"></div>
                </div>
              ) : contactsList.length > 0 ? (
                <div className="space-y-3">
                  {contactsList.map((contact) => (
                    <div
                      key={contact.id}
                      className="bg-surface-card rounded-2xl p-5 border border-border-subtle shadow-sm hover:border-primary-400/40 transition-colors"
                    >
                      <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-3 mb-3">
                        <div>
                          <div className="flex items-center gap-2 mb-1">
                            <span className="font-bold text-text-primary text-base">
                              {contact.name || 'Anonymous User'}
                            </span>
                            <span className="text-xs px-2.5 py-0.5 rounded-full bg-surface-base border border-border-subtle text-text-secondary">
                              {contact.email}
                            </span>
                          </div>
                          <h4 className="text-sm font-semibold text-primary-400">
                            {contact.subject || 'No Subject'}
                          </h4>
                        </div>

                        <div className="flex items-center gap-3 self-end sm:self-auto">
                          <span className="text-[11px] text-text-secondary flex items-center gap-1">
                            <Clock className="w-3 h-3" />
                            {new Date(contact.created_at).toLocaleString()}
                          </span>

                          <button
                            onClick={() => setDeleteTarget({ type: 'contact', item: contact })}
                            title={t('admin.delete')}
                            className="p-1.5 text-text-secondary hover:text-status-dangerText hover:bg-status-dangerBg rounded-lg transition-colors"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </div>
                      </div>

                      <div className="p-3.5 bg-surface-base rounded-xl border border-border-subtle text-xs text-text-secondary leading-relaxed whitespace-pre-wrap">
                        {contact.message}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-16 bg-surface-card rounded-2xl border border-border-subtle">
                  <p className="text-text-secondary text-sm">{t('admin.noContacts')}</p>
                </div>
              )}
            </div>
          )}
        </motion.div>

        {/* Prediction Quick View Modal */}
        <AnimatePresence>
          {selectedPrediction && (
            <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm">
              <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.95 }}
                className="bg-surface-card border border-border-subtle rounded-2xl max-w-2xl w-full p-6 shadow-2xl overflow-hidden"
              >
                <div className="flex items-center justify-between pb-3 border-b border-border-subtle mb-4">
                  <div className="flex items-center gap-2">
                    <Target className="w-5 h-5 text-primary-400" />
                    <h3 className="font-bold text-text-primary text-base">
                      {selectedPrediction.disease_name} ({(selectedPrediction.confidence_score * 100).toFixed(1)}%)
                    </h3>
                  </div>
                  <button
                    onClick={() => setSelectedPrediction(null)}
                    className="p-1 rounded-lg text-text-secondary hover:text-text-primary hover:bg-surface-base"
                  >
                    <X className="w-5 h-5" />
                  </button>
                </div>

                <div className="relative rounded-xl overflow-hidden bg-surface-base border border-border-subtle mb-4 flex items-center justify-center min-h-[260px]">
                  <img
                    src={selectedPrediction.annotated_image_url || selectedPrediction.image_url}
                    alt="Scan preview"
                    className="w-full max-h-[380px] object-contain"
                  />
                </div>

                <div className="grid grid-cols-2 gap-3 text-xs mb-4 p-3 bg-surface-base rounded-xl">
                  <div>
                    <span className="text-text-secondary block">User:</span>
                    <span className="font-semibold text-text-primary">{selectedPrediction.user_name}</span>
                  </div>
                  <div>
                    <span className="text-text-secondary block">Email:</span>
                    <span className="font-semibold text-text-primary">{selectedPrediction.user_email}</span>
                  </div>
                </div>

                <div className="flex items-center justify-end gap-3">
                  <button
                    onClick={() => setSelectedPrediction(null)}
                    className="px-4 py-2 text-xs font-semibold rounded-xl text-text-secondary hover:bg-surface-base"
                  >
                    Close
                  </button>
                  <Link
                    href={`/history/${selectedPrediction.id}`}
                    className="px-4 py-2 text-xs font-semibold rounded-xl bg-primary text-white hover:bg-primary-600 transition-colors flex items-center gap-1.5"
                  >
                    Open Full Diagnosis & PDF <ExternalLink className="w-3.5 h-3.5" />
                  </Link>
                </div>
              </motion.div>
            </div>
          )}
        </AnimatePresence>

        {/* Global Delete Confirmation Modal */}
        <AnimatePresence>
          {deleteTarget && (
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
                      {t('admin.delete')} {deleteTarget.type === 'prediction' ? 'Prediction Scan' : 'Contact Message'}
                    </h3>
                    <p className="text-xs text-text-secondary">
                      This action will permanently delete this record.
                    </p>
                  </div>
                </div>

                <p className="text-sm text-text-secondary mb-6">
                  {deleteTarget.type === 'prediction'
                    ? t('admin.deleteScanConfirm')
                    : t('admin.deleteContactConfirm')}
                </p>

                {deleteError && (
                  <p className="text-xs text-status-dangerText mb-4 bg-status-dangerBg p-2.5 rounded-lg">
                    {deleteError}
                  </p>
                )}

                <div className="flex items-center justify-end gap-3">
                  <button
                    onClick={() => setDeleteTarget(null)}
                    disabled={deleting}
                    className="px-4 py-2 text-sm font-medium text-text-secondary hover:text-text-primary rounded-xl transition-colors"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={handleDeleteConfirm}
                    disabled={deleting}
                    className="px-5 py-2 text-sm font-semibold bg-red-600 text-white rounded-xl hover:bg-red-700 transition-colors disabled:opacity-50 flex items-center gap-2 shadow-lg shadow-red-600/20"
                  >
                    {deleting ? 'Deleting...' : t('admin.delete')}
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
