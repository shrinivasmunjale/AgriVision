'use client'

import { useAuth } from '@/contexts/AuthContext'
import { useRouter, useParams } from 'next/navigation'
import { useEffect, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { predictionsAPI } from '@/lib/api'
import Layout from '@/components/Layout'
import { 
  Download, 
  ArrowLeft, 
  AlertCircle, 
  Trash2, 
  ShieldCheck, 
  Leaf, 
  AlertTriangle, 
  CheckCircle2, 
  Info,
  Pill,
  Sparkles
} from 'lucide-react'
import { motion } from 'framer-motion'
import Link from 'next/link'

import BoundingBoxImage from '@/components/BoundingBoxImage'
import RecommendationCard from '@/components/RecommendationCard'


export default function PredictionDetailPage() {
  const { user, loading, getAccessToken } = useAuth()
  const router = useRouter()
  const params = useParams()
  const predictionId = params.id
  const [downloading, setDownloading] = useState(false)

  useEffect(() => {
    if (!loading && !user) {
      router.push('/auth/login')
    }
  }, [user, loading, router])

  const { data: prediction, isLoading } = useQuery({
    queryKey: ['prediction', predictionId],
    queryFn: async () => {
      const token = await getAccessToken()
      const response = await predictionsAPI.getById(predictionId, token)
      return response.data
    },
    enabled: !!user && !!predictionId,
  })

  const handleDelete = async () => {
    if (!window.confirm('Are you sure you want to delete this prediction record?')) return
    try {
      const token = await getAccessToken()
      await predictionsAPI.deleteById(predictionId, token)
      router.push('/history')
    } catch (error) {
      console.error('Failed to delete prediction:', error)
    }
  }

  const handleDownloadReport = async () => {
    if (downloading) return
    setDownloading(true)
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
    } finally {
      setDownloading(false)
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
            <p className="text-text-secondary">Prediction not found</p>
          </div>
        </div>
      </Layout>
    )
  }

  const isHealthy = prediction.disease_name === 'Healthy' || prediction.disease_name === 'Tomato Healthy'
  const lowConfidence = prediction.confidence_score < 0.6
  const details = prediction.disease_details
  const evidenceRecommendations = details?.evidence_recommendations || []


  return (
    <Layout>
      <div className="p-4 lg:p-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="max-w-5xl mx-auto space-y-6"
        >
          {/* Top Bar Navigation & Actions */}
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <Link
              href="/history"
              className="flex items-center gap-2 text-text-secondary hover:text-text-primary transition-colors text-sm font-medium"
            >
              <ArrowLeft className="w-4 h-4" />
              Back to History
            </Link>
            <div className="flex items-center gap-3">
              <button
                onClick={handleDelete}
                className="flex items-center gap-2 px-4 py-2 bg-red-500/10 hover:bg-red-500/20 text-red-400 border border-red-500/30 rounded-full text-sm font-semibold transition-colors"
              >
                <Trash2 className="w-4 h-4" />
                Delete Record
              </button>
              <button
                onClick={handleDownloadReport}
                disabled={downloading}
                className="flex items-center gap-2 px-5 py-2 bg-primary text-white rounded-full text-sm font-semibold hover:bg-primary-600 transition-all shadow-md active:scale-95 disabled:cursor-wait disabled:opacity-70"
              >
                <Download className={`w-4 h-4 ${downloading ? 'animate-bounce' : ''}`} />
                <span className={downloading ? 'animate-pulse' : ''}>
                  {downloading ? 'Preparing PDF...' : 'Download PDF Report'}
                </span>
              </button>
            </div>
          </div>

          {/* Image Display with Bounding Boxes */}
          <BoundingBoxImage
            src={prediction.image_url}
            alt={prediction.disease_name || 'Leaf scan'}
            boundingBoxes={prediction.bounding_boxes || []}
            defaultDiseaseName={prediction.disease_name}
            defaultConfidence={prediction.confidence_score}
            heightClass="h-[420px]"
            showControls={true}
            showFallbackBox={false}
          />

          {/* Diagnostic Overview Card */}
          <div className="bg-surface-card rounded-2xl p-6 border border-border-subtle shadow-sm">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
              <div>
                <span className="text-xs uppercase tracking-wider text-text-secondary font-semibold">
                  Detected Condition
                </span>
                <div className="flex items-center gap-3 mt-1">
                  <h1 className="text-3xl font-bold text-text-primary">
                    {prediction.disease_name}
                  </h1>
                  <span
                    className={`px-3 py-1 rounded-full text-xs font-semibold ${
                      isHealthy
                        ? 'bg-status-successBg text-status-successText border border-green-500/30'
                        : 'bg-status-dangerBg text-status-dangerText border border-red-500/30'
                    }`}
                  >
                    {isHealthy ? 'Healthy Plant' : (details?.severity ? `${details.severity} Severity` : 'Action Needed')}
                  </span>
                </div>

                {details?.scientific_name && (
                  <p className="text-sm italic text-text-secondary mt-1">
                    Scientific name: {details.scientific_name}
                  </p>
                )}

                {prediction.life_stage && (
                  <p className="text-xs text-primary-400 mt-2 font-medium">
                    Crop Life Stage: {prediction.life_stage} {prediction.crop_age_days ? `(${prediction.crop_age_days} days)` : ''}
                  </p>
                )}
              </div>

              <div className="flex items-center gap-4 bg-surface-base p-4 rounded-xl border border-border-subtle">
                <div className="w-20 h-20 relative">
                  <svg className="transform -rotate-90" width="80" height="80">
                    <circle
                      cx="40"
                      cy="40"
                      r="32"
                      stroke="#3A3F3C"
                      strokeWidth="7"
                      fill="none"
                    />
                    <circle
                      cx="40"
                      cy="40"
                      r="32"
                      stroke={isHealthy ? "#34A65F" : "#10B981"}
                      strokeWidth="7"
                      fill="none"
                      strokeDasharray={`${2 * Math.PI * 32}`}
                      strokeDashoffset={`${
                        2 * Math.PI * 32 * (1 - prediction.confidence_score)
                      }`}
                      strokeLinecap="round"
                    />
                  </svg>
                  <div className="absolute inset-0 flex items-center justify-center">
                    <span className="text-lg font-bold text-text-primary">
                      {(prediction.confidence_score * 100).toFixed(0)}%
                    </span>
                  </div>
                </div>
                <div>
                  <span className="text-xs text-text-secondary block">AI Model Confidence</span>
                  <span className="text-sm font-semibold text-text-primary">
                    {prediction.confidence_score > 0.8 ? 'High Accuracy' : 'Moderate Match'}
                  </span>
                  <span className="text-xs text-text-secondary block mt-1">
                    Scanned: {new Date(prediction.created_at).toLocaleDateString()}
                  </span>
                </div>
              </div>
            </div>

            {lowConfidence && (
              <div className="mt-6 p-4 bg-status-warningBg text-status-warningText rounded-xl flex items-start gap-3 border border-amber-500/30">
                <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
                <p className="text-sm">
                  Low confidence score. Consider retaking the image with better lighting and a close-up focus on leaf symptoms.
                </p>
              </div>
            )}
          </div>

          {/* Structured Knowledge Details from tomato_disease_knowledge.json */}
          {details && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Symptoms */}
              {details.symptoms && details.symptoms.length > 0 && (
                <div className="bg-surface-card rounded-2xl p-6 border border-border-subtle shadow-sm">
                  <div className="flex items-center gap-2 mb-4 text-amber-400 font-bold text-lg">
                    <AlertTriangle className="w-5 h-5" />
                    <h2>Key Symptoms</h2>
                  </div>
                  <ul className="space-y-2">
                    {details.symptoms.map((symptom, i) => (
                      <li key={i} className="flex items-start gap-2.5 text-sm text-text-primary">
                        <span className="w-2 h-2 rounded-full bg-amber-400 mt-2 flex-shrink-0" />
                        <span>{symptom}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Causes */}
              {details.causes && details.causes.length > 0 && (
                <div className="bg-surface-card rounded-2xl p-6 border border-border-subtle shadow-sm">
                  <div className="flex items-center gap-2 mb-4 text-blue-400 font-bold text-lg">
                    <Info className="w-5 h-5" />
                    <h2>Primary Causes</h2>
                  </div>
                  <ul className="space-y-2">
                    {details.causes.map((cause, i) => (
                      <li key={i} className="flex items-start gap-2.5 text-sm text-text-primary">
                        <span className="w-2 h-2 rounded-full bg-blue-400 mt-2 flex-shrink-0" />
                        <span>{cause}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}

          {/* Organic Control & Preventive Measures & Recovery Tips */}
          {details && (
            <div className="space-y-6">
              {/* Organic & Biological Control */}
              {details.organic_control && details.organic_control.length > 0 && (
                <div className="bg-surface-card rounded-2xl p-6 border border-border-subtle shadow-sm">
                  <div className="flex items-center gap-2 mb-4 text-emerald-400 font-bold text-lg">
                    <Leaf className="w-5 h-5" />
                    <h2>Organic & Biological Control</h2>
                  </div>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    {details.organic_control.map((item, i) => (
                      <div key={i} className="p-3.5 bg-emerald-950/20 border border-emerald-500/20 rounded-xl flex items-start gap-3">
                        <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0 mt-0.5" />
                        <span className="text-sm text-text-primary">{item}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Preventive Measures */}
              {details.preventive_measures && details.preventive_measures.length > 0 && (
                <div className="bg-surface-card rounded-2xl p-6 border border-border-subtle shadow-sm">
                  <div className="flex items-center gap-2 mb-4 text-teal-400 font-bold text-lg">
                    <ShieldCheck className="w-5 h-5" />
                    <h2>Preventive Measures</h2>
                  </div>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    {details.preventive_measures.map((item, i) => (
                      <div key={i} className="p-3.5 bg-teal-950/20 border border-teal-500/20 rounded-xl flex items-start gap-3">
                        <CheckCircle2 className="w-4 h-4 text-teal-400 flex-shrink-0 mt-0.5" />
                        <span className="text-sm text-text-primary">{item}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Recovery Tips */}
              {details.recovery_tips && details.recovery_tips.length > 0 && (
                <div className="bg-surface-card rounded-2xl p-6 border border-border-subtle shadow-sm">
                  <div className="flex items-center gap-2 mb-4 text-purple-400 font-bold text-lg">
                    <Sparkles className="w-5 h-5" />
                    <h2>Recovery & Management Tips</h2>
                  </div>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    {details.recovery_tips.map((item, i) => (
                      <div key={i} className="p-3.5 bg-purple-950/20 border border-purple-500/20 rounded-xl flex items-start gap-3">
                        <Info className="w-4 h-4 text-purple-400 flex-shrink-0 mt-0.5" />
                        <span className="text-sm text-text-primary">{item}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {evidenceRecommendations.length > 0 && (
            <section className="bg-surface-card rounded-2xl p-6 border border-border-subtle shadow-sm">
              <div className="flex items-center gap-2 mb-2 text-emerald-400 font-bold text-xl">
                <ShieldCheck className="w-6 h-6" />
                <h2>Evidence-Backed Treatment</h2>
              </div>
              <p className="text-sm text-text-secondary mb-5">
                These are authoritative, evidence-backed treatment references, not a claim of the universally best product.
              </p>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {evidenceRecommendations.map((recommendation) => (
                  <RecommendationCard
                    key={recommendation.id}
                    recommendation={recommendation}
                  />
                ))}
              </div>
              <p className="mt-5 text-xs text-text-secondary border-t border-border-subtle/50 pt-4">
                Recommendations are evidence-backed references. Always follow the current registered product label, local agricultural guidance, crop conditions, safety requirements and applicable regulations before application.
              </p>
            </section>
          )}

          {/* Advisor Link Banner */}
          <div className="bg-gradient-to-r from-emerald-500/10 via-primary/10 to-teal-500/10 border border-emerald-500/20 rounded-2xl p-5 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 shadow-sm">
            <div className="flex items-center gap-3">
              <div className="p-3 bg-emerald-500/20 rounded-xl text-emerald-400">
                <Leaf className="w-6 h-6" />
              </div>
              <div>
                <h3 className="text-base font-bold text-text-primary">Need Tomato Crop Nutrition & Fertilizer Guidance?</h3>
                <p className="text-xs text-text-secondary mt-0.5">
                  Access evidence-backed MPKV Rahuri fertilizer schedules tailored for Hybrid and Improved tomato varieties.
                </p>
              </div>
            </div>
            <Link
              href="/fertilizer-advisor"
              className="inline-flex items-center gap-2 px-4 py-2 bg-primary-500 hover:bg-primary-600 text-white rounded-xl text-xs font-bold transition-all shadow-sm flex-shrink-0"
            >
              <span>Open Fertilizer Advisor</span>
              <Sparkles className="w-3.5 h-3.5" />
            </Link>
          </div>
        </motion.div>
      </div>
    </Layout>
  )
}

