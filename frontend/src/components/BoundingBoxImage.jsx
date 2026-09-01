'use client'

import React, { useState, useRef, useEffect, useCallback } from 'react'
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
 * - showFallbackBox: boolean (default true) - when true and no boxes are
 *   supplied, draw an illustrative focal box. Set to false to never draw
 *   synthetic boxes (the backend now returns tight lesion boxes instead).
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
  showFallbackBox = true,
}) {
  const [showBoxes, setShowBoxes] = useState(true)
  const [showBadges, setShowBadges] = useState(true)
  const [hoveredIndex, setHoveredIndex] = useState(null)
  const [imgError, setImgError] = useState(false)
  const containerRef = useRef(null)
  const imgRef = useRef(null)
  const [imgRect, setImgRect] = useState({ top: 0, left: 0, width: '100%', height: '100%' })

  const updateImgRect = useCallback(() => {
    if (!containerRef.current || !imgRef.current) return
    const container = containerRef.current
    const img = imgRef.current

    const cW = container.clientWidth
    const cH = container.clientHeight
    const nW = img.naturalWidth
    const nH = img.naturalHeight

    if (!cW || !cH || !nW || !nH) {
      setImgRect({ top: 0, left: 0, width: '100%', height: '100%' })
      return
    }

    const imgAspect = nW / nH
    const containerAspect = cW / cH

    let rW, rH, rTop, rLeft
    if (imgAspect < containerAspect) {
      // Taller (portrait) image in wider container
      rH = cH
      rW = cH * imgAspect
      rTop = 0
      rLeft = (cW - rW) / 2
    } else {
      // Wider (landscape) image in taller container
      rW = cW
      rH = cW / imgAspect
      rLeft = 0
      rTop = (cH - rH) / 2
    }

    setImgRect({
      top: `${rTop}px`,
      left: `${rLeft}px`,
      width: `${rW}px`,
      height: `${rH}px`,
    })
  }, [])

  useEffect(() => {
    updateImgRect()
    const handleResize = () => updateImgRect()
    window.addEventListener('resize', handleResize)

    let observer = null
    if (typeof ResizeObserver !== 'undefined' && containerRef.current) {
      observer = new ResizeObserver(() => updateImgRect())
      observer.observe(containerRef.current)
    }

    return () => {
      window.removeEventListener('resize', handleResize)
      if (observer) observer.disconnect()
    }
  }, [src, updateImgRect])

  // Normalize bounding boxes - ensure at most 1 box is selected and verify bounds
  const normalizedBoxes = (boundingBoxes && boundingBoxes.length > 0)
    ? boundingBoxes.slice(0, 1).map((b) => {
        // box_2d format: [ymin, xmin, ymax, xmax] (0.0 to 1.0)
        let ymin = 0.2, xmin = 0.2, ymax = 0.8, xmax = 0.8
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

        // Verification: ensure box does not cover all image
        let bw = xmax - xmin
        let bh = ymax - ymin
        if (bw > 0.78 || bh > 0.78 || (bw * bh) > 0.60) {
          const cx = (xmin + xmax) / 2
          const cy = (ymin + ymax) / 2
          bw = Math.min(bw, 0.65)
          bh = Math.min(bh, 0.65)
          xmin = Math.max(0, cx - bw / 2)
          xmax = Math.min(1, cx + bw / 2)
          ymin = Math.max(0, cy - bh / 2)
          ymax = Math.min(1, cy + bh / 2)
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

  // If no boxes are provided, optionally draw an illustrative focal box.
  const activeBoxes = normalizedBoxes.length > 0 || !showFallbackBox
    ? normalizedBoxes
    : (defaultDiseaseName && !/healthy/i.test(defaultDiseaseName) ? [{
        top: '22%',
        left: '22%',
        width: '56%',
        height: '56%',
        label: defaultDiseaseName,
        confidence: defaultConfidence,
        isHealthy: false,
      }] : [])

  const hasBoxes = activeBoxes.length > 0

  return (
    <div className={`relative w-full rounded-2xl overflow-hidden bg-surface-card border border-border-subtle group ${className}`}>
      {/* Image Display Container */}
      <div
        ref={containerRef}
        className={`relative w-full ${heightClass} flex items-center justify-center bg-surface-base overflow-hidden`}
      >
        <img
          ref={imgRef}
          src={imgError ? '/placeholder-leaf.png' : src}
          alt={alt}
          onLoad={updateImgRect}
          className="w-full h-full object-contain select-none"
          onError={() => setImgError(true)}
        />

        {/* Bounding Box Overlays - precisely positioned over the rendered image */}
        <AnimatePresence>
          {showBoxes && hasBoxes && (
            <div
              style={{
                position: 'absolute',
                top: imgRect.top,
                left: imgRect.left,
                width: imgRect.width,
                height: imgRect.height,
                pointerEvents: 'none',
              }}
            >
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
            {hasBoxes ? 'AI Target Detection: 1 disease region identified' : 'Standard leaf view'}
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
