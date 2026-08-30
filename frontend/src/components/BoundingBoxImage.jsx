'use client'

import React, { useState } from 'react'
import { Eye, EyeOff, Sparkles, Scan, Maximize2, ShieldAlert, CheckCircle2 } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'

/**
 * BoundingBoxImage
 *
 * Props:
 * - src: image URL
 * - alt: image alt text
 * - boundingBoxes: array of { box_2d: [ymin, xmin, ymax, xmax], label: string, confidence: number, disease_id?: number }
 * - defaultDiseaseName: string (fallback label if box has none)
 * - defaultConfidence: number (fallback confidence 0.0 - 1.0)
 * - className: string
 * - heightClass: string (e.g. 'h-96', 'h-64')
 * - showControls: boolean (default true)
 */
export default function BoundingBoxImage({
  src,
  alt = 'Leaf scan',
  boundingBoxes = [],
  defaultDiseaseName = 'Infected Area',
  defaultConfidence = 0.85,
  className = '',
  heightClass = 'h-96',
  showControls = true,
}) {
  const [showBoxes, setShowBoxes] = useState(true)
  const [showBadges, setShowBadges] = useState(true)
  const [hoveredIndex, setHoveredIndex] = useState(null)
  const [imgError, setImgError] = useState(false)

  // Normalize bounding boxes
  const normalizedBoxes = (boundingBoxes && boundingBoxes.length > 0)
    ? boundingBoxes.map((b) => {
        // box_2d format: [ymin, xmin, ymax, xmax] (0.0 to 1.0)
        let ymin = 0.1, xmin = 0.1, ymax = 0.9, xmax = 0.9
        if (Array.isArray(b.box_2d) && b.box_2d.length >= 4) {
          ymin = Math.max(0, Math.min(1, b.box_2d[0]))
          xmin = Math.max(0, Math.min(1, b.box_2d[1]))
          ymax = Math.max(0, Math.min(1, b.box_2d[2]))
          xmax = Math.max(0, Math.min(1, b.box_2d[3]))
        } else if (Array.isArray(b.box) && b.box.length >= 4) {
          ymin = Math.max(0, Math.min(1, b.box[0]))
          xmin = Math.max(0, Math.min(1, b.box[1]))
          ymax = Math.max(0, Math.min(1, b.box[2]))
          xmax = Math.max(0, Math.min(1, b.box[3]))
        }

        const label = b.label || defaultDiseaseName || 'Infected Area'
        const conf = typeof b.confidence === 'number' ? b.confidence : defaultConfidence
        const isHealthy = /healthy/i.test(label)

        return {
          top: `${ymin * 100}%`,
          left: `${xmin * 100}%`,
          width: `${Math.max(4, (xmax - xmin) * 100)}%`,
          height: `${Math.max(4, (ymax - ymin) * 100)}%`,
          label,
          confidence: conf,
          isHealthy,
          raw: b,
        }
      })
    : []

  // If no boxes are provided but disease is detected, construct an illustrative focal box
  const activeBoxes = normalizedBoxes.length > 0 ? normalizedBoxes : (defaultDiseaseName && !/healthy/i.test(defaultDiseaseName) ? [{
    top: '12%',
    left: '12%',
    width: '76%',
    height: '76%',
    label: defaultDiseaseName,
    confidence: defaultConfidence,
    isHealthy: false,
  }] : [])

  const hasBoxes = activeBoxes.length > 0

  return (
    <div className={`relative w-full rounded-2xl overflow-hidden bg-surface-card border border-border-subtle group ${className}`}>
      {/* Controls Bar Header / Overlay */}
      {showControls && (
        <div className="absolute top-3 right-3 z-30 flex items-center gap-2 bg-black/70 backdrop-blur-md px-3 py-1.5 rounded-full border border-white/10 text-xs shadow-lg">
          <button
            type="button"
            onClick={() => setShowBoxes((prev) => !prev)}
            className={`flex items-center gap-1.5 px-2 py-1 rounded-full font-medium transition-all ${
              showBoxes
                ? 'bg-primary-500/30 text-emerald-300 border border-emerald-400/40'
                : 'text-text-secondary hover:text-text-primary'
            }`}
            title="Toggle Bounding Boxes"
          >
            {showBoxes ? <Eye className="w-3.5 h-3.5 text-emerald-400" /> : <EyeOff className="w-3.5 h-3.5" />}
            <span>Bounding Box</span>
          </button>

          {showBoxes && hasBoxes && (
            <button
              type="button"
              onClick={() => setShowBadges((prev) => !prev)}
              className={`flex items-center gap-1 px-2 py-1 rounded-full transition-all ${
                showBadges ? 'text-text-primary font-semibold' : 'text-text-secondary opacity-60'
              }`}
              title="Toggle Confidence Badges"
            >
              <Sparkles className="w-3 h-3 text-amber-400" />
              <span>Confidence</span>
            </button>
          )}

          <div className="w-[1px] h-3.5 bg-white/20" />
          <span className="text-[11px] font-mono text-emerald-400/90 font-semibold px-1">
            {hasBoxes ? `${activeBoxes.length} region${activeBoxes.length > 1 ? 's' : ''}` : 'No box'}
          </span>
        </div>
      )}

      {/* Image Display */}
      <div className={`relative w-full ${heightClass} flex items-center justify-center bg-surface-base overflow-hidden`}>
        <img
          src={imgError ? '/placeholder-leaf.png' : src}
          alt={alt}
          className="w-full h-full object-contain select-none"
          onError={() => setImgError(true)}
        />

        {/* Bounding Box Overlays */}
        <AnimatePresence>
          {showBoxes && hasBoxes && (
            <div className="absolute inset-0 pointer-events-none">
              {activeBoxes.map((box, idx) => {
                const isHovered = hoveredIndex === idx
                const confPercent = Math.round(box.confidence > 1 ? box.confidence : box.confidence * 100)
                const isHealthy = box.isHealthy

                const borderColor = isHealthy
                  ? 'border-emerald-400 ring-emerald-500/40 bg-emerald-500/10'
                  : confPercent >= 80
                  ? 'border-red-500 ring-red-500/40 bg-red-500/10'
                  : 'border-amber-400 ring-amber-500/40 bg-amber-500/10'

                const badgeBg = isHealthy
                  ? 'bg-emerald-600 text-white'
                  : confPercent >= 80
                  ? 'bg-red-600 text-white'
                  : 'bg-amber-600 text-white'

                return (
                  <motion.div
                    key={idx}
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    exit={{ opacity: 0, scale: 0.95 }}
                    transition={{ duration: 0.25, delay: idx * 0.05 }}
                    style={{
                      top: box.top,
                      left: box.left,
                      width: box.width,
                      height: box.height,
                    }}
                    onMouseEnter={() => setHoveredIndex(idx)}
                    onMouseLeave={() => setHoveredIndex(null)}
                    className={`absolute pointer-events-auto border-2 ${borderColor} rounded-xl ring-2 transition-all duration-200 cursor-pointer ${
                      isHovered ? 'ring-4 shadow-2xl scale-[1.01]' : 'shadow-lg'
                    }`}
                  >
                    {/* Pulsing Corner Reticle Markers */}
                    <div className="absolute -top-1 -left-1 w-2.5 h-2.5 border-t-2 border-l-2 border-white rounded-tl-sm shadow" />
                    <div className="absolute -top-1 -right-1 w-2.5 h-2.5 border-t-2 border-r-2 border-white rounded-tr-sm shadow" />
                    <div className="absolute -bottom-1 -left-1 w-2.5 h-2.5 border-b-2 border-l-2 border-white rounded-bl-sm shadow" />
                    <div className="absolute -bottom-1 -right-1 w-2.5 h-2.5 border-b-2 border-r-2 border-white rounded-br-sm shadow" />

                    {/* Floating Confidence Badge on top of Box */}
                    {showBadges && (
                      <motion.div
                        initial={{ y: -6, opacity: 0 }}
                        animate={{ y: 0, opacity: 1 }}
                        className="absolute -top-7 left-0 z-20 flex items-center gap-1.5 shadow-xl select-none"
                      >
                        <div
                          className={`flex items-center gap-1.5 px-2.5 py-0.5 rounded-md text-[11px] font-bold tracking-wide shadow-md ${badgeBg}`}
                        >
                          {isHealthy ? (
                            <CheckCircle2 className="w-3 h-3 text-white" />
                          ) : (
                            <ShieldAlert className="w-3 h-3 text-white" />
                          )}
                          <span>{box.label}</span>
                          <span className="opacity-70">|</span>
                          <span className="font-mono">{confPercent}%</span>
                        </div>
                      </motion.div>
                    )}

                    {/* Hover Detail Card */}
                    {isHovered && (
                      <div className="absolute bottom-2 left-2 z-30 bg-black/85 backdrop-blur-md p-2 rounded-lg border border-white/20 text-xs shadow-2xl pointer-events-none">
                        <div className="font-semibold text-text-primary flex items-center gap-1">
                          <span>{box.label}</span>
                        </div>
                        <div className="text-[11px] text-text-secondary mt-0.5">
                          Detection Confidence: <span className="font-bold text-emerald-400">{confPercent}%</span>
                        </div>
                      </div>
                    )}
                  </motion.div>
                )
              })}
            </div>
          )}
        </AnimatePresence>
      </div>

      {/* Footer Info Strip */}
      <div className="px-4 py-2 bg-surface-card border-t border-border-subtle flex flex-wrap items-center justify-between text-xs text-text-secondary gap-2">
        <div className="flex items-center gap-2">
          <Scan className="w-3.5 h-3.5 text-primary-400" />
          <span>
            {hasBoxes ? `AI Target Detection: ${activeBoxes.length} region(s) identified` : 'Standard leaf view'}
          </span>
        </div>
        {hasBoxes && (
          <div className="flex items-center gap-3 font-medium">
            <span className="flex items-center gap-1">
              <span className="w-2 h-2 rounded-full bg-red-500" /> High Infection
            </span>
            <span className="flex items-center gap-1">
              <span className="w-2 h-2 rounded-full bg-amber-400" /> Moderate
            </span>
            <span className="flex items-center gap-1">
              <span className="w-2 h-2 rounded-full bg-emerald-400" /> Healthy
            </span>
          </div>
        )}
      </div>
    </div>
  )
}
