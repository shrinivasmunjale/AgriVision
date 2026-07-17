'use client'

import { useAuth } from '@/contexts/AuthContext'
import { useRouter, useParams } from 'next/navigation'
import { useEffect } from 'react'
import { useQuery } from '@tanstack/react-query'
import { predictionsAPI } from '@/lib/api'
import Layout from '@/components/Layout'
import { Download, ArrowLeft, AlertCircle } from 'lucide-react'
import { motion } from 'framer-motion'
import Link from 'next/link'

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

  const isHealthy = prediction.disease_name === 'Healthy'
  const lowConfidence = prediction.confidence_score < 0.6

  return (
    <Layout>
      <div className="p-4 lg:p-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="max-w-4xl mx-auto"
        >
          <div className="flex items-center justify-between mb-6">
            <Link
              href="/history"
              className="flex items-center gap-2 text-text-secondary hover:text-text-primary transition-colors"
            >
              <ArrowLeft className="w-5 h-5" />
              Back to History
            </Link>
            <button
              onClick={handleDownloadReport}
              className="flex items-center gap-2 px-4 py-2 bg-primary text-white rounded-full font-semibold hover:bg-primary-600 transition-colors"
            >
              <Download className="w-4 h-4" />
              Download PDF Report
            </button>
          </div>

          <div className="bg-surface-card rounded-2xl overflow-hidden border border-border-subtle mb-6">
            <img
              src={prediction.image_url}
              alt="Leaf scan"
              className="w-full h-96 object-contain bg-surface-base"
            />
          </div>

          <div className="bg-surface-card rounded-2xl p-6 border border-border-subtle mb-6">
            <h2 className="text-2xl font-bold text-text-primary mb-4">
              Diagnostic Results
            </h2>

            <div className="flex items-center justify-between mb-4">
              <div>
                <p className="text-text-secondary text-sm mb-2">Detected Condition</p>
                <span
                  className={`inline-block px-4 py-2 rounded-full text-sm font-medium ${
                    isHealthy
                      ? 'bg-status-successBg text-status-successText'
                      : 'bg-status-dangerBg text-status-dangerText'
                  }`}
                >
                  {prediction.disease_name}
                </span>
              </div>

              <div className="text-right">
                <p className="text-text-secondary text-sm mb-2">Confidence Level</p>
                <div className="flex items-center gap-2">
                  <div className="w-24 h-24 relative">
                    <svg className="transform -rotate-90" width="96" height="96">
                      <circle
                        cx="48"
                        cy="48"
                        r="40"
                        stroke="#3A3F3C"
                        strokeWidth="8"
                        fill="none"
                      />
                      <circle
                        cx="48"
                        cy="48"
                        r="40"
                        stroke="#34A65F"
                        strokeWidth="8"
                        fill="none"
                        strokeDasharray={`${2 * Math.PI * 40}`}
                        strokeDashoffset={`${
                          2 * Math.PI * 40 * (1 - prediction.confidence_score)
                        }`}
                        strokeLinecap="round"
                      />
                    </svg>
                    <div className="absolute inset-0 flex items-center justify-center">
                      <span className="text-2xl font-bold text-text-primary">
                        {(prediction.confidence_score * 100).toFixed(0)}%
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {lowConfidence && (
              <div className="mt-4 p-3 bg-status-warningBg text-status-warningText rounded-lg flex items-start gap-3">
                <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
                <p className="text-sm">
                  Low confidence score. Consider retaking the image with better lighting
                  and focus for more accurate results.
                </p>
              </div>
            )}

            <div className="mt-4 text-text-secondary text-sm">
              <p>
                <strong>Scanned:</strong>{' '}
                {new Date(prediction.created_at).toLocaleDateString('en-US', {
                  month: 'long',
                  day: 'numeric',
                  year: 'numeric',
                  hour: '2-digit',
                  minute: '2-digit',
                })}
              </p>
            </div>
          </div>

          {!isHealthy && prediction.recommendations && prediction.recommendations.length > 0 && (
            <div className="bg-surface-card rounded-2xl p-6 border border-border-subtle">
              <h2 className="text-2xl font-bold text-text-primary mb-4">
                Treatment Recommendations
              </h2>

              {prediction.recommendations.filter((r) => r.pesticide_name).length > 0 && (
                <div className="mb-6">
                  <h3 className="text-lg font-semibold text-text-primary mb-3">
                    Recommended Pesticides
                  </h3>
                  <div className="space-y-3">
                    {prediction.recommendations
                      .filter((r) => r.pesticide_name)
                      .map((rec) => (
                        <div
                          key={rec.id}
                          className="p-4 bg-surface-base rounded-xl border border-border-subtle"
                        >
                          <div className="flex items-start justify-between mb-2">
                            <h4 className="font-semibold text-text-primary">
                              {rec.pesticide_name}
                            </h4>
                            <span className="text-xs text-text-secondary">
                              Match: {(rec.similarity_score * 100).toFixed(0)}%
                            </span>
                          </div>
                        </div>
                      ))}
                  </div>
                </div>
              )}

              {prediction.recommendations.filter((r) => r.fertilizer_name).length > 0 && (
                <div>
                  <h3 className="text-lg font-semibold text-text-primary mb-3">
                    Recommended Fertilizers
                  </h3>
                  <div className="space-y-3">
                    {prediction.recommendations
                      .filter((r) => r.fertilizer_name)
                      .map((rec) => (
                        <div
                          key={rec.id}
                          className="p-4 bg-surface-base rounded-xl border border-border-subtle"
                        >
                          <div className="flex items-start justify-between mb-2">
                            <h4 className="font-semibold text-text-primary">
                              {rec.fertilizer_name}
                            </h4>
                            <span className="text-xs text-text-secondary">
                              Match: {(rec.similarity_score * 100).toFixed(0)}%
                            </span>
                          </div>
                        </div>
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
