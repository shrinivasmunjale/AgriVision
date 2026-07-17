'use client'

import { useAuth } from '@/contexts/AuthContext'
import { useRouter } from 'next/navigation'
import { useEffect, useState } from 'react'
import { predictionsAPI } from '@/lib/api'
import Layout from '@/components/Layout'
import { Upload, X, Loader, AlertCircle } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'

export default function ScanPage() {
  const { user, loading, getAccessToken } = useAuth()
  const router = useRouter()
  const [files, setFiles] = useState([])
  const [previews, setPreviews] = useState([])
  const [uploading, setUploading] = useState(false)
  const [analyzing, setAnalyzing] = useState(false)
  const [error, setError] = useState('')
  const [dragActive, setDragActive] = useState(false)

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

      // Show success message and stay on page to show results
      setAnalyzing(false)
      setFiles([])
      setPreviews([])
      
      // Navigate to history after a short delay to see the success
      setTimeout(() => {
        router.push('/history')
      }, 1000)
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to analyze images')
      setUploading(false)
      setAnalyzing(false)
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
                className="w-full py-4 bg-primary text-white rounded-full font-semibold hover:bg-primary-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
              >
                {uploading ? (
                  <>
                    <Loader className="w-5 h-5 animate-spin" />
                    Uploading Images...
                  </>
                ) : analyzing ? (
                  <>
                    <Loader className="w-5 h-5 animate-spin" />
                    Analyzing Plant Health...
                  </>
                ) : (
                  'Analyze Plant Health'
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
