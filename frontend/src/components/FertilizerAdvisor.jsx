'use client'

import { useState, useEffect } from 'react'
import { Leaf, Sparkles, HelpCircle, FileCheck, AlertCircle, Loader, ArrowRight, RotateCcw } from 'lucide-react'
import { fertilizerRecommendationsAPI } from '@/lib/api'
import FertilizerRecommendationCard from '@/components/FertilizerRecommendationCard'

export default function FertilizerAdvisor() {
  const [crop, setCrop] = useState('Tomato')
  const [varietyType, setVarietyType] = useState('Hybrid')
  const [cropStage, setCropStage] = useState('Recently Transplanted')
  const [hasSoilTest, setHasSoilTest] = useState(false)
  
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')

  const fetchRecommendation = async (vType = varietyType, stage = cropStage, soilTest = hasSoilTest) => {
    setLoading(true)
    setError('')
    try {
      const params = {
        crop: 'Tomato',
        variety_type: vType,
        crop_stage: stage,
        soil_test_available: soilTest,
      }
      const response = await fertilizerRecommendationsAPI.get(params)
      setResult(response.data)
    } catch (err) {
      console.error('Failed to fetch fertilizer recommendation:', err)
      setError('Unable to load recommendation. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  // Load initial recommendation on mount
  useEffect(() => {
    fetchRecommendation('Hybrid', 'Recently Transplanted', false)
  }, [])

  const handleVarietyChange = (val) => {
    setVarietyType(val)
    fetchRecommendation(val, cropStage, hasSoilTest)
  }

  const handleStageChange = (val) => {
    setCropStage(val)
    fetchRecommendation(varietyType, val, hasSoilTest)
  }

  const handleSoilTestToggle = (val) => {
    setHasSoilTest(val)
    fetchRecommendation(varietyType, cropStage, val)
  }

  return (
    <div className="space-y-8">
      {/* Input Selection Form */}
      <div className="bg-surface-card rounded-2xl p-6 sm:p-8 border border-border-subtle shadow-sm space-y-6">
        <div className="flex items-center gap-3 pb-4 border-b border-border-subtle/60">
          <div className="p-3 bg-emerald-500/15 rounded-xl text-emerald-400">
            <Leaf className="w-6 h-6" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-text-primary">Farmer-Friendly Fertilizer Advisor</h2>
            <p className="text-xs text-text-secondary mt-0.5">
              Evidence-backed nutrition schedules from MPKV Rahuri research • No soil test mandatory
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* 1. Tomato Type / Variety */}
          <div className="space-y-3">
            <label className="text-xs font-bold uppercase tracking-wider text-text-secondary block">
              1. Tomato Variety / Type
            </label>
            <div className="space-y-2">
              {[
                { id: 'Hybrid', label: 'Hybrid Tomato' },
                { id: 'Improved Variety', label: 'Improved Variety (सरळ वाण)' },
                { id: "I don't know", label: "I don't know / Not sure" },
              ].map((opt) => (
                <button
                  key={opt.id}
                  type="button"
                  onClick={() => handleVarietyChange(opt.id)}
                  className={`w-full flex items-center justify-between px-4 py-3 rounded-xl border text-xs font-semibold text-left transition-all ${
                    varietyType === opt.id
                      ? 'bg-emerald-500/15 text-emerald-300 border-emerald-500/50 shadow-xs'
                      : 'bg-surface-base text-text-primary border-border-subtle hover:border-primary-400/40'
                  }`}
                >
                  <span>{opt.label}</span>
                  <span className={`w-3.5 h-3.5 rounded-full border flex items-center justify-center ${
                    varietyType === opt.id ? 'border-emerald-400 bg-emerald-400' : 'border-border-subtle'
                  }`}>
                    {varietyType === opt.id && <span className="w-1.5 h-1.5 rounded-full bg-slate-950" />}
                  </span>
                </button>
              ))}
            </div>
          </div>

          {/* 2. Crop Stage */}
          <div className="space-y-3">
            <label className="text-xs font-bold uppercase tracking-wider text-text-secondary block">
              2. Crop Growth Stage
            </label>
            <div className="space-y-2">
              {[
                { id: 'Recently Transplanted', label: 'Recently Transplanted (लागवड)' },
                { id: 'Vegetative Growth', label: 'Vegetative Growth (वाढ अवस्था)' },
                { id: 'Flowering & Fruiting', label: 'Flowering & Fruiting (फुलधारणा/फळधारणा)' },
                { id: "I don't know", label: "I don't know / General Schedule" },
              ].map((opt) => (
                <button
                  key={opt.id}
                  type="button"
                  onClick={() => handleStageChange(opt.id)}
                  className={`w-full flex items-center justify-between px-4 py-3 rounded-xl border text-xs font-semibold text-left transition-all ${
                    cropStage === opt.id
                      ? 'bg-teal-500/15 text-teal-300 border-teal-500/50 shadow-xs'
                      : 'bg-surface-base text-text-primary border-border-subtle hover:border-primary-400/40'
                  }`}
                >
                  <span>{opt.label}</span>
                  <span className={`w-3.5 h-3.5 rounded-full border flex items-center justify-center ${
                    cropStage === opt.id ? 'border-teal-400 bg-teal-400' : 'border-border-subtle'
                  }`}>
                    {cropStage === opt.id && <span className="w-1.5 h-1.5 rounded-full bg-slate-950" />}
                  </span>
                </button>
              ))}
            </div>
          </div>

          {/* 3. Soil Test Report */}
          <div className="space-y-3">
            <label className="text-xs font-bold uppercase tracking-wider text-text-secondary block">
              3. Do you have a Soil Test Report?
            </label>
            <div className="space-y-2">
              <button
                type="button"
                onClick={() => handleSoilTestToggle(false)}
                className={`w-full flex items-center justify-between px-4 py-3 rounded-xl border text-xs font-semibold text-left transition-all ${
                  !hasSoilTest
                    ? 'bg-primary/15 text-primary-300 border-primary/50 shadow-xs'
                    : 'bg-surface-base text-text-primary border-border-subtle hover:border-primary-400/40'
                }`}
              >
                <span>No, use MPKV Research Reference</span>
                <span className={`w-3.5 h-3.5 rounded-full border flex items-center justify-center ${
                  !hasSoilTest ? 'border-primary-400 bg-primary-400' : 'border-border-subtle'
                }`}>
                  {!hasSoilTest && <span className="w-1.5 h-1.5 rounded-full bg-slate-950" />}
                </span>
              </button>

              <button
                type="button"
                onClick={() => handleSoilTestToggle(true)}
                className={`w-full flex items-center justify-between px-4 py-3 rounded-xl border text-xs font-semibold text-left transition-all ${
                  hasSoilTest
                    ? 'bg-primary/15 text-primary-300 border-primary/50 shadow-xs'
                    : 'bg-surface-base text-text-primary border-border-subtle hover:border-primary-400/40'
                }`}
              >
                <span>Yes, I have a Soil Test Report</span>
                <span className={`w-3.5 h-3.5 rounded-full border flex items-center justify-center ${
                  hasSoilTest ? 'border-primary-400 bg-primary-400' : 'border-border-subtle'
                }`}>
                  {hasSoilTest && <span className="w-1.5 h-1.5 rounded-full bg-slate-950" />}
                </span>
              </button>
            </div>

            {hasSoilTest && (
              <div className="p-3 bg-primary/10 border border-primary/20 rounded-xl text-xs text-primary-300 flex items-start gap-2">
                <FileCheck className="w-4 h-4 text-primary-400 flex-shrink-0 mt-0.5" />
                <p>
                  Soil-test report detected. MPKV reference baseline is shown below. For exact soil-based fertilizer titration, consult your local Krishi Vigyan Kendra (KVK).
                </p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Loading state */}
      {loading && (
        <div className="text-center py-12 bg-surface-card rounded-2xl border border-border-subtle">
          <Loader className="w-8 h-8 text-primary-400 animate-spin mx-auto mb-3" />
          <p className="text-sm font-semibold text-text-primary">Fetching MPKV Research Recommendation...</p>
        </div>
      )}

      {/* Error state */}
      {error && (
        <div className="p-4 rounded-xl bg-red-500/10 border border-red-500/30 text-red-300 text-sm flex items-center gap-2">
          <AlertCircle className="w-5 h-5 text-red-400" />
          <span>{error}</span>
        </div>
      )}

      {/* Recommendation Results */}
      {!loading && result && (
        <div className="space-y-6">
          {/* If farmer selected "I don't know" for variety */}
          {result.variety_type === 'Not Specified' || !result.nutrients?.nitrogen?.value ? (
            <div className="p-6 bg-surface-card rounded-2xl border border-border-subtle shadow-sm space-y-4">
              <div className="flex items-start gap-3">
                <div className="p-2.5 bg-amber-500/15 rounded-xl text-amber-400">
                  <HelpCircle className="w-6 h-6" />
                </div>
                <div>
                  <h3 className="text-lg font-bold text-text-primary">General Tomato Fertilizer Guidance</h3>
                  <p className="text-xs text-text-secondary mt-1">
                    Your tomato variety was not specified. MPKV Rahuri provides two distinct research standards:
                  </p>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2">
                <div className="p-4 rounded-xl bg-surface-base border border-border-subtle space-y-2">
                  <h4 className="text-sm font-bold text-emerald-400">Hybrid Tomato (हायब्रिड टोमॅटो)</h4>
                  <p className="text-xs text-text-secondary">
                    FYM @ 20 t/ha + N:P₂O₅:K₂O @ <strong>300:150:150 kg/ha</strong>
                  </p>
                  <button
                    type="button"
                    onClick={() => handleVarietyChange('Hybrid')}
                    className="inline-flex items-center gap-1.5 text-xs font-bold text-primary-400 hover:text-primary-300 mt-2"
                  >
                    <span>View Hybrid Schedule</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </button>
                </div>

                <div className="p-4 rounded-xl bg-surface-base border border-border-subtle space-y-2">
                  <h4 className="text-sm font-bold text-teal-400">Improved Variety (सुधारित वाण)</h4>
                  <p className="text-xs text-text-secondary">
                    FYM @ 20 t/ha + N:P₂O₅:K₂O @ <strong>200:100:100 kg/ha</strong>
                  </p>
                  <button
                    type="button"
                    onClick={() => handleVarietyChange('Improved Variety')}
                    className="inline-flex items-center gap-1.5 text-xs font-bold text-primary-400 hover:text-primary-300 mt-2"
                  >
                    <span>View Improved Variety Schedule</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
            </div>
          ) : (
            <FertilizerRecommendationCard recommendation={result} />
          )}
        </div>
      )}
    </div>
  )
}
