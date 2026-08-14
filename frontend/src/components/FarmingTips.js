'use client'

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Lightbulb, ChevronLeft, ChevronRight } from 'lucide-react'
import Link from 'next/link'
import { miscAPI } from '@/lib/api'

export default function FarmingTips() {
  const [index, setIndex] = useState(0)
  const { data, isLoading } = useQuery({
    queryKey: ['tips'],
    queryFn: async () => {
      const response = await miscAPI.tips()
      return response.data.tips
    },
    staleTime: 10 * 60 * 1000,
  })

  const tips = data || []
  const tip = tips[index]

  const next = () => setIndex((i) => (i + 1) % Math.max(tips.length, 1))
  const prev = () => setIndex((i) => (i - 1 + tips.length) % Math.max(tips.length, 1))

  return (
    <div className="bg-surface-card rounded-2xl p-6 border border-border-subtle flex flex-col">
      <div className="flex items-center justify-between mb-4">
        <h3 className="flex items-center gap-2 font-semibold text-text-primary">
          <Lightbulb className="w-5 h-5 text-accent" /> Farming Tip
        </h3>
        <span className="text-xs text-text-secondary">
          {tips.length > 0 ? `${index + 1}/${tips.length}` : ''}
        </span>
      </div>

      {isLoading ? (
        <p className="text-text-secondary text-sm">Loading tips...</p>
      ) : tip ? (
        <p className="text-text-primary leading-relaxed flex-1 mb-4">{tip}</p>
      ) : (
        <p className="text-text-secondary text-sm">No tips available.</p>
      )}

      <div className="flex items-center justify-between">
        <div className="flex gap-2">
          <button
            onClick={prev}
            className="w-8 h-8 rounded-full bg-surface-base border border-border-subtle flex items-center justify-center text-text-secondary hover:text-primary-400 transition-colors"
            aria-label="Previous tip"
          >
            <ChevronLeft className="w-4 h-4" />
          </button>
          <button
            onClick={next}
            className="w-8 h-8 rounded-full bg-surface-base border border-border-subtle flex items-center justify-center text-text-secondary hover:text-primary-400 transition-colors"
            aria-label="Next tip"
          >
            <ChevronRight className="w-4 h-4" />
          </button>
        </div>
        <Link href="/tips" className="text-sm text-primary-400 hover:underline">
          All tips
        </Link>
      </div>
    </div>
  )
}