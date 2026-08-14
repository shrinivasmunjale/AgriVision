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
  const { lang, setLang } = useI18n()
  const [open, setOpen] = useState(false)

  return (
    <div className={`relative ${className}`}>
      <button
        onClick={() => setOpen((o) => !o)}
        aria-label="Change language"
        className="h-10 px-3 rounded-full flex items-center gap-1.5 bg-surface-card border border-border-subtle text-text-primary hover:border-primary-400/50 transition-colors text-sm font-medium"
      >
        <Languages className="w-4 h-4 text-primary-400" />
        <span className="uppercase">{lang}</span>
        <ChevronDown className={`w-3.5 h-3.5 transition-transform ${open ? 'rotate-180' : ''}`} />
      </button>

      {open && (
        <>
          <div className="fixed inset-0 z-40" onClick={() => setOpen(false)} />
          <div className="absolute right-0 mt-2 z-50 w-40 bg-surface-card border border-border-subtle rounded-xl shadow-xl overflow-hidden">
            {options.map((opt) => (
              <button
                key={opt.code}
                onClick={() => {
                  setLang(opt.code)
                  setOpen(false)
                }}
                className="w-full flex items-center justify-between px-4 py-2.5 text-sm text-text-primary hover:bg-surface-base transition-colors"
              >
                <span>{opt.label}</span>
                {lang === opt.code && <Check className="w-4 h-4 text-primary-400" />}
              </button>
            ))}
          </div>
        </>
      )}
    </div>
  )
}