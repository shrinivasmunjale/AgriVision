'use client'

import { useState } from 'react'
import { Languages, ChevronDown, Check } from 'lucide-react'
import { useI18n } from '@/contexts/I18nContext'

export default function LanguageToggle({ className = '' }) {
  const { lang, setLang, languages } = useI18n()
  const [open, setOpen] = useState(false)

  const currentOpt = languages?.find((o) => o.code === lang) || languages?.[0]

  return (
    <div className={`relative ${className}`}>
      <button
        onClick={() => setOpen((o) => !o)}
        aria-label="Change language"
        className="h-10 px-3.5 rounded-full flex items-center gap-2 bg-surface-card border border-border-subtle text-text-primary hover:border-primary-400/50 transition-colors text-sm font-medium shadow-sm"
      >
        <Languages className="w-4 h-4 text-primary-400" />
        <span className="font-semibold text-xs uppercase">{lang}</span>
        <span className="hidden sm:inline text-xs text-text-secondary">({currentOpt?.native})</span>
        <ChevronDown className={`w-3.5 h-3.5 transition-transform ${open ? 'rotate-180' : ''}`} />
      </button>

      {open && (
        <>
          <div className="fixed inset-0 z-40" onClick={() => setOpen(false)} />
          <div className="absolute right-0 mt-2 z-50 w-52 bg-surface-card border border-border-subtle rounded-2xl shadow-2xl overflow-hidden max-h-80 overflow-y-auto py-1">
            <div className="px-3 py-1.5 text-[10px] font-bold uppercase tracking-wider text-text-secondary border-b border-border-subtle/50 mb-1">
              Select Language / भाषा चुनें
            </div>
            {languages?.map((opt) => (
              <button
                key={opt.code}
                onClick={() => {
                  setLang(opt.code)
                  setOpen(false)
                }}
                className={`w-full flex items-center justify-between px-3.5 py-2 text-xs text-left transition-colors ${
                  lang === opt.code
                    ? 'bg-primary/10 text-primary-400 font-semibold'
                    : 'text-text-primary hover:bg-surface-base'
                }`}
              >
                <div className="flex items-center gap-2">
                  <span className="font-medium">{opt.native}</span>
                  <span className="text-[11px] text-text-secondary">({opt.label})</span>
                </div>
                {lang === opt.code && <Check className="w-4 h-4 text-primary-400 flex-shrink-0" />}
              </button>
            ))}
          </div>
        </>
      )}
    </div>
  )
}