'use client'

import { useState } from 'react'
import { Languages, ChevronDown, Check } from 'lucide-react'
import { useI18n } from '@/contexts/I18nContext'

const options = [
  { code: 'en', label: 'English' },
  { code: 'hi', label: 'हिन्दी' },
  { code: 'es', label: 'Español' },
]

export default function LanguageToggle({ className = '' }) {
  const { lang, setLang, languages } = useI18n()
  const [open, setOpen] = useState(false)
  const currentLang = languages?.find((l) => l.code === lang) || { code: lang, native: lang.toUpperCase() }

  return (
    <div className={`relative ${className}`}>
      <button
        onClick={() => setOpen((o) => !o)}
        aria-label="Change language"
        className="h-10 px-3.5 rounded-full flex items-center gap-2 bg-surface-card border border-border-subtle text-text-primary hover:border-primary-400 transition-colors text-sm font-medium shadow-sm"
      >
        <Languages className="w-4 h-4 text-primary-400" />
        <span className="font-semibold">{currentLang.native}</span>
        <ChevronDown className={`w-3.5 h-3.5 text-text-secondary transition-transform ${open ? 'rotate-180' : ''}`} />
      </button>

      {open && (
        <>
          <div className="fixed inset-0 z-40" onClick={() => setOpen(false)} />
          <div className="absolute right-0 mt-2 z-50 w-56 max-h-80 overflow-y-auto bg-surface-card border border-border-subtle rounded-2xl shadow-2xl p-1.5 scrollbar-thin">
            <div className="px-3 py-2 text-xs font-semibold text-text-secondary uppercase tracking-wider border-b border-border-subtle mb-1">
              Select Language / भाषा
            </div>
            {languages?.map((opt) => {
              const isActive = lang === opt.code
              return (
                <button
                  key={opt.code}
                  onClick={() => {
                    setLang(opt.code)
                    setOpen(false)
                  }}
                  className={`w-full flex items-center justify-between px-3 py-2 rounded-xl text-sm transition-colors ${
                    isActive
                      ? 'bg-primary-400/15 text-primary-400 font-bold'
                      : 'text-text-primary hover:bg-surface-base'
                  }`}
                >
                  <div className="flex flex-col text-left">
                    <span className="font-medium text-sm">{opt.native}</span>
                    <span className="text-[11px] text-text-secondary">{opt.label}</span>
                  </div>
                  {isActive && <Check className="w-4 h-4 text-primary-400 flex-shrink-0" />}
                </button>
              )
            })}
          </div>
        </>
      )}
    </div>
  )
}