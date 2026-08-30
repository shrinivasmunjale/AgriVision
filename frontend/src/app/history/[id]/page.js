'use client'

import { useAuth } from '@/contexts/AuthContext'
import { useRouter, useParams } from 'next/navigation'
import { useEffect, useState } from 'react'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { predictionsAPI } from '@/lib/api'
import Layout from '@/components/Layout'
import {
  Download,
  ArrowLeft,
  AlertCircle,
  Target,
  Eye,
  Trash2,
  ShieldAlert,
  Clock,
  Sparkles,
  Droplet,
  Info,
  CheckCircle2,
  Calendar
} from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import { useI18n } from '@/contexts/I18nContext'
import Link from 'next/link'

export default function PredictionDetailPage() {
  const { user, loading, getAccessToken, profile } = useAuth()
  const router = useRouter()
  const params = useParams()
  const predictionId = params.id
  const queryClient = useQueryClient()
  const { t } = useI18n()
  const [viewMode, setViewMode] = useState('annotated')
  const [showDeleteModal, setShowDeleteModal] = useState(false)
  const [deleting, setDeleting] = useState(false)
  const [deleteError, setDeleteError] = useState('')

  useEffect(() => {
    if (!loading) {
      if (!user) router.push('/auth/login')
      else if (profile?.role === 'admin') router.push('/admin')
    }
  }, [user, loading, profile, router])

  const { data: prediction, isLoading } = useQuery({
    queryKey: ['prediction', predictionId],
    queryFn: async () => {
      const token = await getAccessToken()
      const response = await predictionsAPI.getById(predictionId, token)
      return response.data
    },
    enabled: !!user && !!predictionId,
  })

  const handleDownloadReport = async () => {
    try {
      const token = await getAccessToken()
      const response = await predictionsAPI.downloadReport(predictionId, token)
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', `agrivision_report_${predictionId}.pdf`)
      document.body.appendChild(link)
      link.click()
      link.remove()
    } catch (error) {
      console.error('Failed to download report:', error)
    }
  }

  const handleDelete = async () => {
    setDeleting(true)
    setDeleteError('')
    try {
      const token = await getAccessToken()
      await predictionsAPI.delete(predictionId, token)
      await queryClient.invalidateQueries({ queryKey: ['predictions'] })
      await queryClient.invalidateQueries({ queryKey: ['all-predictions'] })
      router.push('/history')
    } catch (err) {
      console.error('Failed to delete prediction:', err)
      setDeleteError(err.response?.data?.detail || 'Failed to delete scan record')
      setDeleting(false)
    }
  }

  if (loading || !user || isLoading) {
    return (
      <Layout>
        <div className="flex items-center justify-center min-h-screen">
          <div className="w-16 h-16 border-4 border-primary-400 border-t-transparent rounded-full animate-spin"></div>
        </div>
      </Layout>
    )
  }

  if (!prediction) {
    return (
      <Layout>
        <div className="p-4 lg:p-8">
          <div className="text-center py-12">
            <AlertCircle className="w-16 h-16 text-text-secondary mx-auto mb-4" />
            <p className="text-text-secondary">{t('history.noPredictions')}</p>
          </div>
        </div>
      </Layout>
    )
  }

  const isHealthy = prediction.disease_name === 'Healthy'
  const lowConfidence = prediction.confidence_score < 0.6
  const displayImage =
    viewMode === 'annotated' && prediction.annotated_image_url
      ? prediction.annotated_image_url
      : prediction.image_url

  const pesticideRecs = prediction.recommendations?.filter((r) => r.pesticide_name) || []
  const fertilizerRecs = prediction.recommendations?.filter((r) => r.fertilizer_name) || []
  const advisoryNote = pesticideRecs.find((r) => r.recommendation_note)?.recommendation_note || ''
  const cropStage = pesticideRecs.find((r) => r.crop_stage)?.crop_stage || ''

  return (
    <Layout>
      <div className="p-4 lg:p-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="max-w-4xl mx-auto"
        >
          {/* Top Actions Bar */}
          <div className="flex flex-wrap items-center justify-between gap-3 mb-6">
            <Link
              href="/history"
              className="flex items-center gap-2 text-text-secondary hover:text-text-primary transition-colors text-sm font-medium"
            >
              <ArrowLeft className="w-4 h-4" />
              {t('history.back')}
            </Link>
            <div className="flex items-center gap-2">
              <button
                onClick={handleDownloadReport}
                className="flex items-center gap-2 px-4 py-2 bg-primary-400/15 text-primary-400 border border-primary-400/30 rounded-xl font-semibold hover:bg-primary-400/25 transition-colors text-sm shadow-sm"
              >
                <Download className="w-4 h-4" />
                {t('history.downloadReport')}
              </button>
              <button
                onClick={() => setShowDeleteModal(true)}
                className="flex items-center gap-1.5 px-3.5 py-2 bg-status-dangerBg text-status-dangerText border border-status-dangerText/20 rounded-xl font-semibold hover:bg-red-500/20 transition-colors text-sm"
              >
                <Trash2 className="w-4 h-4" />
                {t('history.delete')}
              </button>
            </div>
          </div>

          {/* Leaf Detection Image Card */}
          <div className="bg-surface-card rounded-2xl overflow-hidden border border-border-subtle mb-6 p-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-3 px-1">
              <div className="flex items-center gap-2">
                <Target className="w-5 h-5 text-primary-400" />
                <span className="font-semibold text-text-primary text-sm">
                  {t('scan.leafWithDetection')}
                </span>
              </div>
              <div className="flex bg-surface-base p-1 rounded-xl border border-border-subtle text-xs font-semibold self-start sm:self-auto">
                <button
                  onClick={() => setViewMode('annotated')}
                  className={`px-3 py-1.5 rounded-lg flex items-center gap-1.5 transition-colors ${
                    viewMode === 'annotated'
                      ? 'bg-primary-400 text-white shadow'
                      : 'text-text-secondary hover:text-text-primary'
                  }`}
                >
                  <Target className="w-3.5 h-3.5" />
                  YOLO Bounding Box
                </button>
                <button
                  onClick={() => setViewMode('original')}
                  className={`px-3 py-1.5 rounded-lg flex items-center gap-1.5 transition-colors ${
                    viewMode === 'original'
                      ? 'bg-primary-400 text-white shadow'
                      : 'text-text-secondary hover:text-text-primary'
                  }`}
                >
                  <Eye className="w-3.5 h-3.5" />
                  Original
                </button>
              </div>
            </div>

            <div className="relative rounded-xl overflow-hidden bg-surface-base border border-border-subtle flex items-center justify-center min-h-[280px]">
              <img
                src={displayImage}
                alt="Leaf scan with YOLO bounding box"
                className="w-full max-h-[420px] object-contain bg-surface-base transition-all duration-300"
              />
              {prediction.annotated_image_url && viewMode === 'annotated' && (
                <div className="absolute top-3 left-3 bg-black/80 backdrop-blur-md px-3 py-1.5 rounded-full border border-primary-400/40 text-xs text-white font-medium flex items-center gap-1.5 shadow-lg">
                  <span className="w-2 h-2 rounded-full bg-red-500 animate-pulse"></span>
                  YOLO Infection Target
                </div>
              )}
            </div>
          </div>

          {/* Diagnostic Results Card */}
          <div className="bg-surface-card rounded-2xl p-6 border border-border-subtle mb-6">
            <h2 className="text-xl font-bold text-text-primary mb-4">
              {t('history.diagnosticResults')}
            </h2>

            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-6 pb-4 border-b border-border-subtle">
              <div>
                <p className="text-text-secondary text-xs uppercase tracking-wider mb-2 font-semibold">
                  {t('history.detectedCondition')}
                </p>
                <div className="flex items-center gap-2">
                  <span
                    className={`inline-block px-4 py-2 rounded-xl text-base font-bold ${
                      isHealthy
                        ? 'bg-status-successBg text-status-successText'
                        : 'bg-status-dangerBg text-status-dangerText'
                    }`}
                  >
                    {prediction.disease_name}
                  </span>
                  {cropStage && (
                    <span className="px-3 py-1.5 rounded-lg bg-surface-base border border-border-subtle text-xs text-text-secondary font-medium">
                      Stage: {cropStage}
                    </span>
                  )}
                </div>
              </div>

              <div className="flex items-center gap-4">
                <div className="text-right">
                  <p className="text-text-secondary text-xs uppercase tracking-wider mb-1 font-semibold">
                    {t('history.confidenceLevel')}
                  </p>
                  <p className="text-2xl font-black text-text-primary">
                    {(prediction.confidence_score * 100).toFixed(1)}%
                  </p>
                </div>
                <div className="w-16 h-16 relative flex-shrink-0">
                  <svg className="transform -rotate-90" width="64" height="64">
                    <circle cx="32" cy="32" r="26" stroke="#3A3F3C" strokeWidth="6" fill="none" />
                    <circle
                      cx="32"
                      cy="32"
                      r="26"
                      stroke={isHealthy ? '#34A65F' : '#E5484D'}
                      strokeWidth="6"
                      fill="none"
                      strokeDasharray={`${2 * Math.PI * 26}`}
                      strokeDashoffset={`${2 * Math.PI * 26 * (1 - prediction.confidence_score)}`}
                      strokeLinecap="round"
                    />
                  </svg>
                  <div className="absolute inset-0 flex items-center justify-center">
                    <span className="text-xs font-bold text-text-primary">
                      {(prediction.confidence_score * 100).toFixed(0)}%
                    </span>
                  </div>
                </div>
              </div>
            </div>

            {lowConfidence && (
              <div className="mt-4 p-3.5 bg-status-warningBg text-status-warningText rounded-xl flex items-start gap-3 border border-status-warningText/20">
                <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
                <p className="text-sm">
                  Low confidence score. Consider retaking the image with better lighting and focus for more accurate results.
                </p>
              </div>
            )}

            {advisoryNote && (
              <div className="mt-4 p-4 bg-primary-400/10 border border-primary-400/25 rounded-xl flex items-start gap-3">
                <Info className="w-5 h-5 text-primary-400 flex-shrink-0 mt-0.5" />
                <div>
                  <h4 className="text-sm font-semibold text-primary-400 mb-0.5">
                    {t('history.specialAdvisory')}
                  </h4>
                  <p className="text-sm text-text-secondary">{advisoryNote}</p>
                </div>
              </div>
            )}

            <div className="mt-4 flex items-center gap-2 text-text-secondary text-xs">
              <Calendar className="w-3.5 h-3.5" />
              <span>
                <strong>{t('history.scanned')}:</strong>{' '}
                {new Date(prediction.created_at).toLocaleDateString('en-US', {
                  month: 'long',
                  day: 'numeric',
                  year: 'numeric',
                  hour: '2-digit',
                  minute: '2-digit',
                })}
              </span>
            </div>
          </div>

          {/* Treatment Recommendations from pesticides.json */}
          {!isHealthy && (
            <div className="bg-surface-card rounded-2xl p-6 border border-border-subtle mb-6">
              <div className="flex items-center gap-2 mb-6">
                <Sparkles className="w-6 h-6 text-primary-400" />
                <h2 className="text-xl font-bold text-text-primary">
                  {t('history.treatmentRecs')}
                </h2>
              </div>

              {pesticideRecs.length > 0 ? (
                <div className="mb-8">
                  <h3 className="text-sm font-bold uppercase tracking-wider text-text-secondary mb-4 flex items-center gap-2">
                    <Droplet className="w-4 h-4 text-primary-400" />
                    {t('history.recommendedPesticides')} ({pesticideRecs.length})
                  </h3>

                  <div className="space-y-4">
                    {pesticideRecs.map((rec, idx) => (
                      <div
                        key={idx}
                        className="p-5 bg-surface-base rounded-2xl border border-border-subtle hover:border-primary-400/40 transition-colors shadow-sm"
                      >
                        {/* Header: Name, Priority Badge, Match */}
                        <div className="flex flex-wrap items-center justify-between gap-2 mb-3">
                          <div className="flex items-center gap-2.5 flex-wrap">
                            <span className="px-2.5 py-1 rounded-lg bg-primary-400/20 text-primary-400 text-xs font-bold">
                              #{rec.priority || idx + 1} {t('history.priority')}
                            </span>
                            <h4 className="text-lg font-bold text-text-primary">
                              {rec.pesticide_name}
                            </h4>
                            {rec.type && (
                              <span className="px-2.5 py-0.5 rounded-full bg-surface-card text-text-secondary border border-border-subtle text-xs">
                                {rec.type}
                              </span>
                            )}
                          </div>
                          {rec.effectiveness && (
                            <span className="px-2.5 py-1 rounded-lg bg-status-successBg text-status-successText text-xs font-semibold">
                              {t('history.effectiveness')}: {rec.effectiveness}
                            </span>
                          )}
                        </div>

                        {/* Detailed Grid: Active ingredient, Dosage, Spray Interval, Application */}
                        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-3 p-3.5 bg-surface-card/60 rounded-xl border border-border-subtle mb-3 text-xs">
                          {rec.active_ingredient && (
                            <div>
                              <span className="text-text-secondary block font-medium">
                                {t('history.activeIngredient')}
                              </span>
                              <span className="font-semibold text-text-primary">
                                {rec.active_ingredient}
                              </span>
                            </div>
                          )}
                          {rec.dosage && (
                            <div>
                              <span className="text-text-secondary block font-medium">
                                {t('history.dosage')}
                              </span>
                              <span className="font-semibold text-text-primary">
                                {rec.dosage}
                              </span>
                            </div>
                          )}
                          {rec.spray_interval && (
                            <div>
                              <span className="text-text-secondary block font-medium">
                                {t('history.sprayInterval')}
                              </span>
                              <span className="font-semibold text-text-primary">
                                {rec.spray_interval}
                              </span>
                            </div>
                          )}
                          {rec.application_method && (
                            <div>
                              <span className="text-text-secondary block font-medium">
                                {t('history.applicationMethod')}
                              </span>
                              <span className="font-semibold text-text-primary">
                                {rec.application_method}
                              </span>
                            </div>
                          )}
                        </div>

                        {/* Waiting period & Precautions */}
                        <div className="space-y-2 text-xs">
                          {rec.waiting_period && (
                            <div className="flex items-center gap-1.5 text-text-secondary">
                              <Clock className="w-3.5 h-3.5 text-status-warningText" />
                              <span>
                                <strong className="text-text-primary">{t('history.waitingPeriod')}:</strong>{' '}
                                {rec.waiting_period}
                              </span>
                            </div>
                          )}

                          {rec.precautions && rec.precautions.length > 0 && (
                            <div className="pt-2 border-t border-border-subtle/60">
                              <span className="font-semibold text-text-secondary flex items-center gap-1.5 mb-1.5">
                                <ShieldAlert className="w-3.5 h-3.5 text-primary-400" />
                                {t('history.precautions')}:
                              </span>
                              <ul className="list-disc list-inside space-y-1 text-text-secondary pl-1">
                                {rec.precautions.map((prec, pIdx) => (
                                  <li key={pIdx}>{prec}</li>
                                ))}
                              </ul>
                            </div>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              ) : null}

              {fertilizerRecs.length > 0 && (
                <div>
                  <h3 className="text-sm font-bold uppercase tracking-wider text-text-secondary mb-4 flex items-center gap-2">
                    <Sparkles className="w-4 h-4 text-primary-400" />
                    {t('history.recommendedFertilizers')}
                  </h3>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    {fertilizerRecs.map((rec, idx) => (
                      <div
                        key={idx}
                        className="p-4 bg-surface-base rounded-xl border border-border-subtle"
                      >
                        <div className="flex items-start justify-between mb-2">
                          <h4 className="font-bold text-text-primary">{rec.fertilizer_name}</h4>
                          <span className="text-xs px-2 py-0.5 bg-primary-400/10 text-primary-400 rounded-full font-semibold">
                            {rec.application_stage || 'All Stages'}
                          </span>
                        </div>
                        {rec.composition && (
                          <p className="text-xs text-text-secondary mb-1">
                            <strong>Composition:</strong> {rec.composition}
                          </p>
                        )}
                        {rec.dosage && (
                          <p className="text-xs text-text-secondary">
                            <strong>Dosage:</strong> {rec.dosage}
                          </p>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {isHealthy && (
            <div className="bg-surface-card rounded-2xl p-6 border border-border-subtle mb-6 text-center py-8">
              <CheckCircle2 className="w-12 h-12 text-status-successText mx-auto mb-3" />
              <h3 className="text-lg font-bold text-text-primary mb-1">Crops are Healthy!</h3>
              <p className="text-sm text-text-secondary max-w-md mx-auto">
                No pesticide application is needed at this time. Maintain regular irrigation, balanced nutrition, and routine crop scouting.
              </p>
            </div>
          )}
        </motion.div>

        {/* Delete Confirmation Modal */}
        <AnimatePresence>
          {showDeleteModal && (
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
                      {t('history.delete')} Scan
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
                    onClick={() => setShowDeleteModal(false)}
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
