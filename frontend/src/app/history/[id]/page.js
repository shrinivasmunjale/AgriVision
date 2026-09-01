'use client'

import { useAuth } from '@/contexts/AuthContext'
import { useRouter, useParams } from 'next/navigation'
import { useEffect } from 'react'
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

export default function PredictionDetailPage() {
  const { user, loading, getAccessToken } = useAuth()
  const router = useRouter()
  const params = useParams()
  const predictionId = params.id

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
  const pesticideRecommendations = (prediction.recommendations || []).filter((item) => item.pesticide_name)
  const fertilizerRecommendations = (prediction.recommendations || []).filter((item) => item.fertilizer_name)

  const formatLifeStages = (value) => {
    if (!value) return null
    if (Array.isArray(value)) return value.join(', ')
    return String(value).replace(/[\[\]"]/g, '').split(',').map((stage) => stage.trim()).filter(Boolean).join(', ')
  }

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
                className="flex items-center gap-2 px-5 py-2 bg-primary text-white rounded-full text-sm font-semibold hover:bg-primary-600 transition-all shadow-md active:scale-95"
              >
                <Download className="w-4 h-4" />
                Download PDF Report
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

          {/* Detailed Recommended Pesticides from tomato_disease_knowledge.json */}
          {details?.recommended_pesticides && details.recommended_pesticides.length > 0 && (
            <div className="bg-surface-card rounded-2xl p-6 border border-border-subtle shadow-sm">
              <div className="flex items-center gap-2 mb-4 text-primary-400 font-bold text-xl">
                <Pill className="w-6 h-6" />
                <h2>Recommended Chemical Treatment & Dosages</h2>
              </div>
              <div className="space-y-4">
                {details.recommended_pesticides.map((pest, idx) => (
                  <div key={idx} className="p-5 bg-surface-base border border-border-subtle rounded-xl space-y-3">
                    <div className="flex flex-wrap items-center justify-between gap-2 border-b border-border-subtle/50 pb-3">
                      <h3 className="text-lg font-semibold text-text-primary">
                        {pest.name}
                      </h3>
                      {pest.application_method && (
                        <span className="px-3 py-1 bg-primary/10 text-primary-400 rounded-full text-xs font-medium border border-primary/20">
                          {pest.application_method}
                        </span>
                      )}
                    </div>

                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm">
                      {pest.dosage && (
                        <div>
                          <strong className="text-text-secondary block text-xs">Recommended Dosage:</strong>
                          <span className="text-text-primary font-medium">{pest.dosage}</span>
                        </div>
                      )}
                      {pest.frequency && (
                        <div>
                          <strong className="text-text-secondary block text-xs">Application Frequency:</strong>
                          <span className="text-text-primary font-medium">{pest.frequency}</span>
                        </div>
                      )}
                    </div>

                    {pest.how_to_use && pest.how_to_use.length > 0 && (
                      <div className="pt-2">
                        <strong className="text-text-secondary block text-xs mb-1">How to Use:</strong>
                        <ul className="list-disc list-inside space-y-1 text-sm text-text-primary pl-1">
                          {pest.how_to_use.map((step, sIdx) => (
                            <li key={sIdx}>{step}</li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {pest.precautions && pest.precautions.length > 0 && (
                      <div className="pt-2">
                        <strong className="text-amber-400/90 block text-xs mb-1 font-semibold">Safety Precautions:</strong>
                        <ul className="list-disc list-inside space-y-1 text-xs text-text-secondary pl-1">
                          {pest.precautions.map((prec, pIdx) => (
                            <li key={pIdx}>{prec}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Nutrient recommendations from the disease treatment plan */}
          {details?.recommended_fertilizers && details.recommended_fertilizers.length > 0 && (
            <div className="bg-surface-card rounded-2xl p-6 border border-border-subtle shadow-sm">
              <div className="flex items-center gap-2 mb-4 text-emerald-400 font-bold text-xl">
                <Leaf className="w-6 h-6" />
                <h2>Recommended Fertilizers & Recovery Nutrition</h2>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {details.recommended_fertilizers.map((fertilizer, idx) => (
                  <div key={idx} className="p-5 bg-surface-base border border-border-subtle rounded-xl space-y-3">
                    <h3 className="text-lg font-semibold text-text-primary">{fertilizer.name}</h3>
                    {fertilizer.purpose && <p className="text-sm text-text-secondary">{fertilizer.purpose}</p>}
                    <div className="grid grid-cols-1 gap-3 text-sm border-t border-border-subtle/50 pt-3">
                      {fertilizer.dosage && <div><strong className="text-text-secondary block text-xs">Recommended Dosage</strong><span className="text-text-primary font-medium">{fertilizer.dosage}</span></div>}
                      {fertilizer.application_method && <div><strong className="text-text-secondary block text-xs">Application Method</strong><span className="text-text-primary font-medium">{fertilizer.application_method}</span></div>}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Saved input recommendations: the same source used by the PDF report. */}
          {!isHealthy && (pesticideRecommendations.length > 0 || fertilizerRecommendations.length > 0) && (
            <div className="bg-surface-card rounded-2xl p-6 border border-border-subtle shadow-sm">
              <div className="flex items-center gap-2 mb-2 text-primary-400 font-bold text-xl">
                <Pill className="w-6 h-6" />
                <h2>Selected Recommendations</h2>
              </div>
              <p className="text-sm text-text-secondary mb-5">Product details, dosage, and application guidance for this scan.</p>

              {pesticideRecommendations.length > 0 && (
                <div className="mb-6">
                  <h3 className="text-base font-semibold text-text-primary mb-3">Pesticides</h3>
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                    {pesticideRecommendations.map((rec) => (
                      <RecommendationCard key={rec.id} recommendation={rec} name={rec.pesticide_name} label="Pesticide" formatLifeStages={formatLifeStages} />
                    ))}
                  </div>
                </div>
              )}

              {fertilizerRecommendations.length > 0 && (
                <div>
                  <h3 className="text-base font-semibold text-text-primary mb-3">Fertilizers</h3>
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                    {fertilizerRecommendations.map((rec) => (
                      <RecommendationCard key={rec.id} recommendation={rec} name={rec.fertilizer_name} label="Fertilizer" formatLifeStages={formatLifeStages} />
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </motion.div>
      </div>
    </Layout>
  )
}

function RecommendationCard({ recommendation, name, label, formatLifeStages }) {
  const fields = [
    ['Active Ingredient', recommendation.active_ingredient],
    ['Recommended Dosage', recommendation.dosage],
    ['Application Method', recommendation.application_method],
    ['Suitable Life Stages', formatLifeStages(recommendation.suitable_life_stages)],
  ].filter(([, value]) => value)

  return (
    <article className="p-5 bg-surface-base border border-border-subtle rounded-xl">
      <div className="flex items-start justify-between gap-3 border-b border-border-subtle/50 pb-3 mb-4">
        <div>
          <span className="text-xs font-semibold uppercase tracking-wider text-text-secondary">{label}</span>
          <h4 className="text-lg font-semibold text-text-primary mt-1">{name}</h4>
        </div>
        <span className="shrink-0 px-3 py-1 bg-primary/10 text-primary-400 rounded-full text-xs font-semibold border border-primary/20">
          Match {Math.round((recommendation.similarity_score || 0) * 100)}%
        </span>
      </div>
      <dl className="grid grid-cols-1 sm:grid-cols-2 gap-x-5 gap-y-4 text-sm">
        {fields.map(([field, value]) => (
          <div key={field}>
            <dt className="text-xs text-text-secondary mb-1">{field}</dt>
            <dd className="text-text-primary font-medium">{value}</dd>
          </div>
        ))}
      </dl>
    </article>
  )
}
