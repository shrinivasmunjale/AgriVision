'use client'

import { useAuth } from '@/contexts/AuthContext'
import { useRouter } from 'next/navigation'
import { useEffect, useRef, useState, useMemo } from 'react'
import { useQueryClient } from '@tanstack/react-query'
import { predictionsAPI } from '@/lib/api'
import Layout from '@/components/Layout'
import {
  Upload,
  X,
  Loader,
  AlertCircle,
  Camera as CameraIcon,
  Layers,
  CheckCircle,
  ExternalLink,
  RotateCcw,
  Sparkles,
  Target
} from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import { useI18n } from '@/contexts/I18nContext'
import Link from 'next/link'

export default function ScanPage() {
  const { user, loading, getAccessToken, profile } = useAuth()
  const router = useRouter()
  const queryClient = useQueryClient()
  const { t } = useI18n()
  const [files, setFiles] = useState([])
  const [previews, setPreviews] = useState([])
  const [uploading, setUploading] = useState(false)
  const [analyzing, setAnalyzing] = useState(false)
  const [error, setError] = useState('')
  const [dragActive, setDragActive] = useState(false)
  const [batchResults, setBatchResults] = useState(null)
  const cameraInputRef = useRef(null)

  useEffect(() => {
    if (!loading) {
      if (!user) router.push('/auth/login')
      else if (profile?.role === 'admin') router.push('/admin')
    }
  }, [user, loading, profile, router])

  const handleFileSelect = (selectedFiles) => {
    const fileArray = Array.from(selectedFiles)
    const validFiles = fileArray.filter((file) => file.type.startsWith('image/'))

    if (validFiles.length !== fileArray.length) {
      setError('Only image files are allowed')
      return
    }

    if (files.length + validFiles.length > 50) {
      setError('Maximum 50 images allowed')
      return
    }

    setFiles([...files, ...validFiles])
    
    validFiles.forEach((file) => {
      const reader = new FileReader()
      reader.onloadend = () => {
        setPreviews((prev) => [...prev, reader.result])
      }
      reader.readAsDataURL(file)
    })

    setError('')
    setBatchResults(null)
  }

  const handleDrag = (e) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true)
    } else if (e.type === 'dragleave') {
      setDragActive(false)
    }
  }

  const handleDrop = (e) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)

    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFileSelect(e.dataTransfer.files)
    }
  }

  const removeFile = (index) => {
    setFiles(files.filter((_, i) => i !== index))
    setPreviews(previews.filter((_, i) => i !== index))
  }

  const handleAnalyze = async () => {
    if (files.length === 0) return

    setUploading(true)
    setError('')

    try {
      const token = await getAccessToken()

      const formData = new FormData()
      files.forEach((file) => {
        formData.append('files', file)
      })

      const uploadResponse = await predictionsAPI.uploadImages(formData, token)
      const imageUrls = uploadResponse.data.uploaded_urls

      setUploading(false)
      setAnalyzing(true)

      const analyzeResponse = await predictionsAPI.analyze(
        { image_urls: imageUrls },
        token
      )

      setAnalyzing(false)
      setFiles([])
      setPreviews([])
      
      // Invalidate React Query cache so fresh data is immediately displayed without reloading
      await queryClient.invalidateQueries({ queryKey: ['predictions'] })
      await queryClient.invalidateQueries({ queryKey: ['all-predictions'] })

      const newPredictions = analyzeResponse.data?.predictions
      if (newPredictions && newPredictions.length > 0) {
        if (newPredictions.length === 1) {
          // Direct navigation if single image
          router.push(`/history/${newPredictions[0].id}`)
        } else {
          // Display batch grouped disease summary if multi-image upload
          setBatchResults(newPredictions)
        }
      } else {
        router.push('/history')
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to analyze images')
      setUploading(false)
      setAnalyzing(false)
    }
  }

  // Compute disease groups from multi-image batch results
  const diseaseGroups = useMemo(() => {
    if (!batchResults) return []
    const groups = {}
    batchResults.forEach((pred) => {
      const key = pred.disease_name || 'Unknown'
      if (!groups[key]) {
        groups[key] = {
          name: key,
          items: [],
          recommendations: pred.recommendations || [],
        }
      }
      groups[key].items.push(pred)
    })

    return Object.values(groups).map((grp) => {
      const sumConf = grp.items.reduce((acc, curr) => acc + curr.confidence_score, 0)
      grp.avgConfidence = grp.items.length > 0 ? sumConf / grp.items.length : 0
      return grp
    })
  }, [batchResults])

  if (loading || !user) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-primary-400 border-t-transparent rounded-full animate-spin mx-auto"></div>
        </div>
      </div>
    )
  }

  if (profile?.role === 'admin') {
    return null
  }

  return (
    <Layout>
      <div className="p-4 lg:p-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="max-w-4xl mx-auto"
        >
          <h1 className="text-3xl font-bold text-text-primary mb-2">
            Scan Tomato Leaves
          </h1>
          <p className="text-text-secondary mb-8">
            Upload single or multiple images of tomato leaves for AI-powered disease detection & YOLO bounding box analysis
          </p>

          {error && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className="mb-6 p-4 bg-status-dangerBg text-status-dangerText rounded-xl flex items-start gap-3"
            >
              <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
              <p>{error}</p>
            </motion.div>
          )}

          {/* MULTI-IMAGE BATCH RESULTS GROUPED BY DISEASE */}
          {batchResults && batchResults.length > 0 ? (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="mb-10 space-y-6"
            >
              <div className="bg-surface-card rounded-2xl p-6 border border-border-subtle flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <Sparkles className="w-5 h-5 text-primary-400" />
                    <h2 className="text-xl font-bold text-text-primary">
                      Batch Analysis Complete
                    </h2>
                  </div>
                  <p className="text-sm text-text-secondary">
                    Analyzed <span className="font-semibold text-text-primary">{batchResults.length} leaves</span> across{' '}
                    <span className="font-semibold text-primary-400">{diseaseGroups.length} disease category groups</span>
                  </p>
                </div>
                <div className="flex items-center gap-3">
                  <button
                    onClick={() => setBatchResults(null)}
                    className="inline-flex items-center gap-2 px-4 py-2 bg-surface-base border border-border-subtle rounded-xl text-sm font-semibold text-text-primary hover:border-primary-400/50 transition-colors"
                  >
                    <RotateCcw className="w-4 h-4 text-text-secondary" />
                    New Scan
                  </button>
                  <Link
                    href="/history"
                    className="inline-flex items-center gap-2 px-4 py-2 bg-primary text-white rounded-xl text-sm font-semibold hover:bg-primary-600 transition-colors"
                  >
                    <Layers className="w-4 h-4" />
                    View History
                  </Link>
                </div>
              </div>

              {/* Grouped by Disease Cards */}
              <div className="space-y-6">
                {diseaseGroups.map((group) => {
                  const isHealthy = group.name === 'Healthy'
                  return (
                    <div
                      key={group.name}
                      className="bg-surface-card rounded-2xl border border-border-subtle p-6 space-y-4"
                    >
                      {/* Group Header */}
                      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-4 border-b border-border-subtle">
                        <div className="flex items-center gap-3">
                          <span
                            className={`w-3.5 h-3.5 rounded-full ${
                              isHealthy ? 'bg-status-successText' : 'bg-status-dangerText'
                            }`}
                          ></span>
                          <div>
                            <h3 className="text-lg font-bold text-text-primary">
                              {group.name}
                            </h3>
                            <p className="text-xs text-text-secondary">
                              {group.items.length} {group.items.length === 1 ? 'Leaf' : 'Leaves'} with similar condition • Avg Confidence: {(group.avgConfidence * 100).toFixed(1)}%
                            </p>
                          </div>
                        </div>
                        <span
                          className={`px-3 py-1 rounded-full text-xs font-semibold self-start sm:self-auto ${
                            isHealthy
                              ? 'bg-status-successBg text-status-successText'
                              : 'bg-status-dangerBg text-status-dangerText'
                          }`}
                        >
                          {isHealthy ? 'Healthy Target' : 'Infection Detected'}
                        </span>
                      </div>

                      {/* Image items in this disease group */}
                      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
                        {group.items.map((item) => (
                          <Link
                            key={item.id}
                            href={`/history/${item.id}`}
                            className="group block bg-surface-base rounded-xl overflow-hidden border border-border-subtle hover:border-primary-400 transition-colors"
                          >
                            <div className="aspect-video relative overflow-hidden bg-surface-card">
                              <img
                                src={item.annotated_image_url || item.image_url}
                                alt="Leaf analysis"
                                className="w-full h-full object-cover group-hover:scale-105 transition-transform"
                              />
                              {item.annotated_image_url && (
                                <div className="absolute top-2 right-2 bg-black/75 backdrop-blur-sm px-2 py-0.5 rounded-full text-[10px] text-white font-semibold flex items-center gap-1 border border-white/20">
                                  <span className="w-1.5 h-1.5 rounded-full bg-red-400 animate-pulse"></span>
                                  YOLO BBox
                                </div>
                              )}
                            </div>
                            <div className="p-3 flex items-center justify-between">
                              <span className="text-xs text-text-secondary">Confidence</span>
                              <span className="text-xs font-bold text-text-primary flex items-center gap-1">
                                {(item.confidence_score * 100).toFixed(1)}%
                                <ExternalLink className="w-3 h-3 text-primary-400" />
                              </span>
                            </div>
                          </Link>
                        ))}
                      </div>

                      {/* Shared Recommendations for this disease group */}
                      {!isHealthy && group.recommendations && group.recommendations.length > 0 && (
                        <div className="mt-4 pt-4 border-t border-border-subtle bg-surface-base/50 p-4 rounded-xl">
                          <p className="text-xs font-bold text-text-primary uppercase tracking-wide mb-2">
                            🌿 Group Treatment Recommendations:
                          </p>
                          <div className="flex flex-wrap gap-2">
                            {group.recommendations.map((rec, i) => {
                              const label = rec.pesticide_name || rec.fertilizer_name
                              if (!label) return null
                              return (
                                <span
                                  key={i}
                                  className="text-xs bg-surface-card border border-border-subtle px-3 py-1.5 rounded-lg text-text-primary font-medium"
                                >
                                  {label} ({((rec.similarity_score || 0.9) * 100).toFixed(0)}% match)
                                </span>
                              )
                            })}
                          </div>
                        </div>
                      )}
                    </div>
                  )
                })}
              </div>
            </motion.div>
          ) : (
            /* UPLOAD CONTROLS */
            <>
              <div
                onDragEnter={handleDrag}
                onDragLeave={handleDrag}
                onDragOver={handleDrag}
                onDrop={handleDrop}
                className={`relative border-2 border-dashed rounded-2xl p-12 text-center transition-colors ${
                  dragActive
                    ? 'border-primary-400 bg-primary-400/10'
                    : 'border-border-subtle bg-surface-card'
                }`}
              >
                <input
                  type="file"
                  multiple
                  accept="image/*"
                  onChange={(e) => handleFileSelect(e.target.files)}
                  className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                  disabled={uploading || analyzing}
                />
                <Upload className="w-16 h-16 text-text-secondary mx-auto mb-4" />
                <p className="text-text-primary font-semibold mb-2">
                  Drop images here or click to upload
                </p>
                <p className="text-text-secondary text-sm mb-1">
                  PNG, JPG, or TIFF (max 15MB per file, up to 50 files)
                </p>
                <p className="text-primary-400 text-xs">
                  🚁 Supports multiple images & drone-captured aerial imagery
                </p>
              </div>

              {/* Camera capture */}
              <div className="mt-4 flex flex-col sm:flex-row items-center justify-center gap-3">
                <input
                  ref={cameraInputRef}
                  type="file"
                  accept="image/*"
                  capture="environment"
                  onChange={(e) => handleFileSelect(e.target.files)}
                  className="hidden"
                  disabled={uploading || analyzing}
                />
                <button
                  onClick={() => cameraInputRef.current?.click()}
                  disabled={uploading || analyzing}
                  className="inline-flex items-center gap-2 px-5 py-2.5 bg-surface-card border border-border-subtle rounded-full font-semibold text-text-primary hover:border-primary-400/50 transition-colors disabled:opacity-50"
                >
                  <CameraIcon className="w-5 h-5 text-primary-400" />
                  Capture with Camera
                </button>
              </div>

              {previews.length > 0 && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="mt-8"
                >
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-lg font-semibold text-text-primary">
                      Selected Images ({files.length})
                    </h3>
                    <span className="text-xs text-primary-400 font-medium">
                      Multi-image batch analysis will group similar diseases automatically
                    </span>
                  </div>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                    <AnimatePresence>
                      {previews.map((preview, index) => (
                        <motion.div
                          key={index}
                          initial={{ opacity: 0, scale: 0.8 }}
                          animate={{ opacity: 1, scale: 1 }}
                          exit={{ opacity: 0, scale: 0.8 }}
                          className="relative group"
                        >
                          <img
                            src={preview}
                            alt={`Preview ${index + 1}`}
                            className="w-full h-32 object-cover rounded-xl"
                          />
                          <button
                            onClick={() => removeFile(index)}
                            className="absolute top-2 right-2 w-6 h-6 bg-red-500 text-white rounded-full flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity"
                          >
                            <X className="w-4 h-4" />
                          </button>
                        </motion.div>
                      ))}
                    </AnimatePresence>
                  </div>

                  <button
                    onClick={handleAnalyze}
                    disabled={uploading || analyzing || files.length === 0}
                    className="w-full py-4 bg-primary text-white rounded-full font-semibold hover:bg-primary-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 shadow-lg"
                  >
                    {uploading ? (
                      <>
                        <Loader className="w-5 h-5 animate-spin" />
                        Uploading Images...
                      </>
                    ) : analyzing ? (
                      <>
                        <Loader className="w-5 h-5 animate-spin" />
                        Analyzing & Grouping Similar Diseases...
                      </>
                    ) : (
                      `Analyze ${files.length} ${files.length === 1 ? 'Leaf' : 'Leaves'} with YOLO Detection`
                    )}
                  </button>
                </motion.div>
              )}

              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 }}
                className="mt-12 bg-surface-card rounded-2xl p-6 border border-border-subtle"
              >
                <h3 className="text-lg font-semibold text-text-primary mb-4">
                  Tips for Accurate Results
                </h3>
                <ul className="space-y-3">
                  <li className="flex items-start gap-3">
                    <div className="w-6 h-6 bg-primary-400/20 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                      <span className="text-primary-400 text-sm font-bold">1</span>
                    </div>
                    <p className="text-text-secondary">
                      Ensure good lighting - avoid harsh shadows or backlight
                    </p>
                  </li>
                  <li className="flex items-start gap-3">
                    <div className="w-6 h-6 bg-primary-400/20 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                      <span className="text-primary-400 text-sm font-bold">2</span>
                    </div>
                    <p className="text-text-secondary">
                      Capture clear, focused images of the leaf surface
                    </p>
                  </li>
                  <li className="flex items-start gap-3">
                    <div className="w-6 h-6 bg-primary-400/20 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                      <span className="text-primary-400 text-sm font-bold">3</span>
                    </div>
                    <p className="text-text-secondary">
                      Upload multiple leaves from the same plant or field to group similar diseases together
                    </p>
                  </li>
                </ul>
              </motion.div>
            </>
          )}
        </motion.div>
      </div>
    </Layout>
  )
}
