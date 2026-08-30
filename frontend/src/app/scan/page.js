'use client'

import { useAuth } from '@/contexts/AuthContext'
import { useRouter } from 'next/navigation'
import { useEffect, useRef, useState } from 'react'
import { useQueryClient } from '@tanstack/react-query'
import { predictionsAPI } from '@/lib/api'
import Layout from '@/components/Layout'
import { Upload, X, Loader, AlertTriangle, Camera as CameraIcon, Sparkles, Leaf, Download, ExternalLink } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import { useI18n } from '@/contexts/I18nContext'
import Link from 'next/link'
import BoundingBoxImage from '@/components/BoundingBoxImage'

export default function ScanPage() {
  const { user, loading, getAccessToken } = useAuth()
  const router = useRouter()
  const queryClient = useQueryClient()
  const { t } = useI18n()
  const [files, setFiles] = useState([])
  const [previews, setPreviews] = useState([])
  const [uploading, setUploading] = useState(false)
  const [analyzing, setAnalyzing] = useState(false)
  const [error, setError] = useState('')
  const [dragActive, setDragActive] = useState(false)
  const [results, setResults] = useState(null)
  const [ignoredModalOpen, setIgnoredModalOpen] = useState(false)
  const cameraInputRef = useRef(null)

  const metricTone = {
    default: 'bg-surface-card border-border-subtle text-text-primary',
    green: 'bg-emerald-500/10 border-emerald-500/30 text-emerald-300',
    amber: 'bg-amber-500/10 border-amber-500/30 text-amber-300',
    red: 'bg-red-500/10 border-red-500/30 text-red-300',
  }

  useEffect(() => {
    if (!loading && !user) {
      router.push('/auth/login')
    }
  }, [user, loading, router])

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
    if (files.length <= 1) {
      setError('')
    }
  }

  const handleAnalyze = async () => {
    if (files.length === 0) return

    setUploading(true)
    setError('')
    setResults(null)

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
        {
          image_urls: imageUrls,
          filenames: files.map((f) => f.name || 'image'),
        },
        token
      )

      setAnalyzing(false)

      const data = analyzeResponse.data
      setResults(data)
      setIgnoredModalOpen((data.ignored_images?.length || 0) > 0)

      setFiles([])
      setPreviews([])

      // Invalidate React Query cache so fresh data is immediately displayed
      await queryClient.invalidateQueries({ queryKey: ['predictions'] })
      await queryClient.invalidateQueries({ queryKey: ['all-predictions'] })
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to analyze images')
      setUploading(false)
      setAnalyzing(false)
    }
  }

  const handleDownloadReport = async () => {
    if (!results) return
    setError('')
    try {
      const token = await getAccessToken()
      const payload = {
        total_uploaded: results.total_uploaded || 0,
        processed: results.processed || 0,
        ignored: results.ignored || 0,
        healthy: results.healthy || 0,
        infected: results.infected || 0,
        disease_summary: results.disease_summary || {},
        ignored_images: results.ignored_images || [],
        valid_predictions: results.valid_predictions || results.predictions || [],
      }
      const resp = await predictionsAPI.downloadBatchReport(payload, token)
      const blob = new Blob([resp.data], { type: 'application/pdf' })
      const url = URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = 'agrivision_batch_report.pdf'
      link.click()
      URL.revokeObjectURL(url)
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to download report')
    }
  }

  if (loading || !user) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-primary-400 border-t-transparent rounded-full animate-spin mx-auto"></div>
        </div>
      </div>
    )
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
            Upload images of tomato leaves for AI-powered disease detection • Supports drone-captured aerial imagery
          </p>

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
              🚁 Supports drone-captured aerial imagery for large field analysis
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

          {/* Selected Images Section */}
          {previews.length > 0 && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="mt-8"
            >
              <h3 className="text-lg font-semibold text-text-primary mb-4">
                Selected Images ({files.length})
              </h3>
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
                        className="w-full h-32 object-cover rounded-xl border border-border-subtle"
                      />
                      <button
                        onClick={() => removeFile(index)}
                        className="absolute top-2 right-2 w-6 h-6 bg-red-500 text-white rounded-full flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity shadow-lg"
                      >
                        <X className="w-4 h-4" />
                      </button>
                    </motion.div>
                  ))}
                </AnimatePresence>
              </div>

              {/* Warning alert displayed DIRECTLY ABOVE the Analyze button */}
              <AnimatePresence>
                {error && (
                  <motion.div
                    initial={{ opacity: 0, y: -10, scale: 0.98 }}
                    animate={{ opacity: 1, y: 0, scale: 1 }}
                    exit={{ opacity: 0, y: -10 }}
                    className="mb-4 p-4 bg-amber-500/15 border-2 border-amber-500/40 text-amber-300 rounded-2xl flex items-start gap-3.5 shadow-xl backdrop-blur-md"
                  >
                    <div className="p-2 bg-amber-500/20 rounded-xl flex-shrink-0">
                      <AlertTriangle className="w-6 h-6 text-amber-400" />
                    </div>
                    <div className="text-sm font-medium leading-relaxed pt-1">
                      {error}
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>

              {/* Redesigned Premium "Analyze Plant Health" Button */}
              <button
                onClick={handleAnalyze}
                disabled={uploading || analyzing || files.length === 0}
                className="w-full py-4.5 px-8 bg-gradient-to-r from-emerald-500 via-primary-400 to-green-600 hover:from-emerald-400 hover:to-green-500 text-white rounded-2xl font-bold text-lg shadow-xl shadow-emerald-500/20 hover:shadow-emerald-500/35 hover:scale-[1.01] active:scale-[0.99] transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100 flex items-center justify-center gap-3 border border-emerald-400/30"
              >
                {uploading ? (
                  <>
                    <Loader className="w-6 h-6 animate-spin" />
                    <span>Uploading Images...</span>
                  </>
                ) : analyzing ? (
                  <>
                    <Loader className="w-6 h-6 animate-spin" />
                    <span>Analyzing Plant Health...</span>
                  </>
                ) : (
                  <>
                    {/* <Sparkles className="w-6 h-6 text-emerald-100 animate-pulse" /> */}
                    <span>{t('scan.analyze')}</span>
                    {/* <Leaf className="w-5 h-5 text-emerald-100" /> */}
                  </>
                )}
              </button>
            </motion.div>
          )}

          {/* Batch Results Section */}
          {results && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="mt-8 bg-surface-card rounded-2xl p-6 border border-border-subtle shadow-xl"
            >
              <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
                <h2 className="text-2xl font-bold text-text-primary">Batch Analysis Results</h2>
                <div className="flex flex-wrap gap-3">
                  <button
                    onClick={handleDownloadReport}
                    className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-primary-400 text-white font-semibold text-sm hover:bg-primary-500 transition-colors"
                  >
                    <Download className="w-4 h-4" /> Download PDF Report
                  </button>
                  <button
                    onClick={() => setResults(null)}
                    className="inline-flex items-center gap-2 px-4 py-2 rounded-xl border border-border-subtle text-text-secondary font-semibold text-sm hover:border-primary-400/50 transition-colors"
                  >
                    Scan Again
                  </button>
                </div>
              </div>

              {/* Metrics Bar */}
              <div className="grid grid-cols-2 md:grid-cols-5 gap-3 mb-6">
                {[
                  { label: 'Total Uploaded', value: results.total_uploaded, tone: 'default' },
                  { label: 'Processed', value: results.processed, tone: 'green' },
                  { label: 'Ignored', value: results.ignored, tone: 'amber' },
                  { label: 'Healthy', value: results.healthy, tone: 'green' },
                  { label: 'Infected', value: results.infected, tone: 'red' },
                ].map((m) => (
                  <div key={m.label} className={`p-3 rounded-2xl border text-center ${metricTone[m.tone]}`}>
                    <div className="text-2xl font-bold">{m.value ?? 0}</div>
                    <div className="text-xs font-medium mt-1 opacity-80">{m.label}</div>
                  </div>
                ))}
              </div>

              {/* Detected Leaves with Bounding Boxes */}
              {((results.valid_predictions && results.valid_predictions.length > 0) || (results.predictions && results.predictions.length > 0)) && (
                <div className="mb-6">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-lg font-semibold text-text-primary">
                      Analyzed Leaves & Infected Regions ({(results.valid_predictions || results.predictions).length})
                    </h3>
                    <span className="text-xs text-primary-400 font-medium">
                      🎯 AI Target & Confidence Overlays
                    </span>
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {(results.valid_predictions || results.predictions).map((pred, idx) => {
                      const isHealthy = /healthy/i.test(pred.disease_name || '')
                      return (
                        <div
                          key={pred.id || idx}
                          className="bg-surface-base rounded-2xl p-4 border border-border-subtle hover:border-primary-400/40 transition-all flex flex-col justify-between shadow-sm"
                        >
                          <div className="mb-3">
                            <BoundingBoxImage
                              src={pred.image_url}
                              alt={pred.disease_name || 'Detected leaf'}
                              boundingBoxes={pred.bounding_boxes || []}
                              defaultDiseaseName={pred.disease_name}
                              defaultConfidence={pred.confidence_score}
                              heightClass="h-56"
                              showControls={true}
                            />
                          </div>

                          <div className="flex items-center justify-between pt-2 border-t border-border-subtle/60">
                            <div>
                              <div className="text-sm font-bold text-text-primary">
                                {pred.disease_name || 'Detected Plant'}
                              </div>
                              <div className="text-xs text-text-secondary">
                                Accuracy: <span className="font-semibold text-emerald-400">{Math.round((pred.confidence_score || 0) * 100)}%</span>
                              </div>
                            </div>

                            {pred.id && (
                              <Link
                                href={`/history/${pred.id}`}
                                className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-primary/10 hover:bg-primary/20 text-primary-400 border border-primary/20 rounded-full text-xs font-semibold transition-colors"
                              >
                                <span>Details</span>
                                <ExternalLink className="w-3.5 h-3.5" />
                              </Link>
                            )}
                          </div>
                        </div>
                      )
                    })}
                  </div>
                </div>
              )}

              {/* Grouped Disease View */}
              {Object.keys(results.disease_summary || {}).length > 0 && (
                <div className="mb-6">
                  <h3 className="text-lg font-semibold text-text-primary mb-4">Detection Summary</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {Object.entries(results.disease_summary).map(([disease, files]) => {
                      const isHealthy = /healthy/i.test(disease)
                      return (
                        <div
                          key={disease}
                          className={`rounded-2xl p-4 border ${
                            isHealthy
                              ? 'bg-emerald-500/10 border-emerald-500/30'
                              : 'bg-red-500/5 border-red-500/20'
                          }`}
                        >
                          <div className="flex items-center justify-between mb-2">
                            <span className="font-semibold text-text-primary">{disease}</span>
                            <span
                              className={`text-xs px-2 py-0.5 rounded-full font-semibold ${
                                isHealthy
                                  ? 'bg-emerald-500/20 text-emerald-300'
                                  : 'bg-red-500/20 text-red-300'
                              }`}
                            >
                              {files.length}
                            </span>
                          </div>
                          <ul className="space-y-1">
                            {files.map((f, i) => (
                              <li key={i} className="text-sm text-text-secondary truncate">• {f}</li>
                            ))}
                          </ul>
                        </div>
                      )
                    })}
                  </div>
                </div>
              )}

              {/* Ignored Images */}
              {results.ignored_images && results.ignored_images.length > 0 && (
                <div>
                  <h3 className="text-lg font-semibold text-text-primary mb-4">Ignored Images</h3>
                  <div className="space-y-2">
                    {results.ignored_images.map((item, i) => (
                      <div
                        key={i}
                        className="flex items-start gap-3 p-3 rounded-xl border border-amber-500/30 bg-amber-500/10"
                      >
                        <AlertTriangle className="w-5 h-5 text-amber-400 flex-shrink-0 mt-0.5" />
                        <div>
                          <div className="text-sm font-semibold text-amber-200">{item.filename}</div>
                          <div className="text-sm text-amber-300/80">{item.reason}</div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </motion.div>
          )}

          <AnimatePresence>
            {ignoredModalOpen && results?.ignored_images?.length > 0 && (
              <motion.div
                className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                role="dialog"
                aria-modal="true"
                aria-labelledby="ignored-images-title"
              >
                <motion.div
                  className="w-full max-w-lg rounded-2xl border border-amber-500/30 bg-surface-card p-6 shadow-2xl"
                  initial={{ opacity: 0, scale: 0.95, y: 16 }}
                  animate={{ opacity: 1, scale: 1, y: 0 }}
                  exit={{ opacity: 0, scale: 0.95, y: 16 }}
                >
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex items-start gap-3">
                      <div className="rounded-full bg-amber-500/15 p-2">
                        <AlertTriangle className="h-6 w-6 text-amber-400" />
                      </div>
                      <div>
                        <h2 id="ignored-images-title" className="text-xl font-semibold text-text-primary">Some images were ignored</h2>
                        <p className="mt-1 text-sm text-text-secondary">These images could not be analyzed reliably. Try a clear, well-lit tomato-leaf photo.</p>
                      </div>
                    </div>
                    <button type="button" onClick={() => setIgnoredModalOpen(false)} className="rounded-lg p-1 text-text-secondary transition hover:bg-white/10 hover:text-text-primary" aria-label="Close ignored images message">
                      <X className="h-5 w-5" />
                    </button>
                  </div>
                  <div className="mt-5 max-h-56 space-y-2 overflow-y-auto pr-1">
                    {results.ignored_images.map((item, index) => (
                      <div key={`${item.filename}-${index}`} className="rounded-xl bg-amber-500/10 p-3">
                        <p className="truncate text-sm font-medium text-amber-200">{item.filename}</p>
                        <p className="mt-1 text-sm text-amber-300/80">{item.reason}</p>
                      </div>
                    ))}
                  </div>
                  <button type="button" onClick={() => setIgnoredModalOpen(false)} className="mt-6 w-full rounded-xl bg-amber-500 px-4 py-2.5 font-semibold text-slate-950 transition hover:bg-amber-400">Got it</button>
                </motion.div>
              </motion.div>
            )}
          </AnimatePresence>

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
                  Include multiple angles for comprehensive analysis
                </p>
              </li>
            </ul>
          </motion.div>
        </motion.div>
      </div>
    </Layout>
  )
}
