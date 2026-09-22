'use client'

import { ShieldCheck, ExternalLink, Info, AlertCircle, CheckCircle2, FileText, Building2, FlaskConical } from 'lucide-react'

export function getEvidenceBadgeConfig(sourceType = '') {
  const type = (sourceType || '').toLowerCase()

  if (type.includes('government pesticide') || type.includes('government_label') || type.includes('ppqs')) {
    return {
      label: '✓ GOVERNMENT PESTICIDE LABEL',
      badgeClass: 'bg-emerald-500/15 text-emerald-300 border-emerald-500/40',
      iconClass: 'text-emerald-400',
    }
  }
  if (type.includes('government agricultural') || type.includes('government_advisory')) {
    return {
      label: '✓ GOVERNMENT AGRICULTURAL ADVISORY',
      badgeClass: 'bg-teal-500/15 text-teal-300 border-teal-500/40',
      iconClass: 'text-teal-400',
    }
  }
  if (type.includes('icar') || type.includes('icar_research')) {
    return {
      label: '✓ ICAR RESEARCH SOURCE',
      badgeClass: 'bg-sky-500/15 text-sky-300 border-sky-500/40',
      iconClass: 'text-sky-400',
    }
  }
  if (type.includes('university') || type.includes('agricultural_university') || type.includes('tnau')) {
    return {
      label: '✓ AGRICULTURAL UNIVERSITY SOURCE',
      badgeClass: 'bg-blue-500/15 text-blue-300 border-blue-500/40',
      iconClass: 'text-blue-400',
    }
  }
  if (type.includes('manage') || type.includes('indian')) {
    return {
      label: '✓ INDIAN AGRICULTURAL SOURCE',
      badgeClass: 'bg-cyan-500/15 text-cyan-300 border-cyan-500/40',
      iconClass: 'text-cyan-400',
    }
  }
  if (type.includes('international') || type.includes('pacific')) {
    return {
      label: 'ℹ INTERNATIONAL AGRICULTURAL SOURCE',
      badgeClass: 'bg-amber-500/15 text-amber-300 border-amber-500/40',
      iconClass: 'text-amber-400',
    }
  }
  if (type.includes('ipm') || type.includes('sanitation') || type.includes('vector')) {
    return {
      label: 'ℹ IPM / DISEASE MANAGEMENT',
      badgeClass: 'bg-purple-500/15 text-purple-300 border-purple-500/40',
      iconClass: 'text-purple-400',
    }
  }
  if (type.includes('monitoring') || type.includes('healthy') || type.includes('no_treatment')) {
    return {
      label: '✓ NO CHEMICAL TREATMENT',
      badgeClass: 'bg-emerald-500/15 text-emerald-300 border-emerald-500/40',
      iconClass: 'text-emerald-400',
    }
  }

  return {
    label: `✓ ${sourceType.toUpperCase() || 'EVIDENCE SOURCE'}`,
    badgeClass: 'bg-primary/10 text-primary-300 border-primary/30',
    iconClass: 'text-primary-400',
  }
}

export default function RecommendationCard({ recommendation, className = '' }) {
  if (!recommendation) return null

  const source = recommendation.source || {}
  const badge = getEvidenceBadgeConfig(source.source_type)

  const doseFormatted = [recommendation.dose, recommendation.dose_unit].filter(Boolean).join(' ')

  const specs = [
    { label: 'Formulation', value: recommendation.formulation },
    { label: 'Dose', value: doseFormatted },
    { label: 'Water Volume', value: recommendation.water_volume },
    { label: 'Application Method', value: recommendation.application_method },
    { label: 'Crop Stage', value: recommendation.crop_stage },
    { label: 'Application Frequency', value: recommendation.frequency },
    { label: 'Pre-Harvest Interval (PHI)', value: recommendation.pre_harvest_interval },
    { label: 'Re-entry Period', value: recommendation.re_entry_period },
  ].filter((item) => Boolean(item.value))

  return (
    <article
      className={`rounded-2xl border border-border-subtle bg-surface-card p-5 shadow-sm transition-all hover:border-primary-400/40 ${className}`}
    >
      {/* Header: Type and Badge */}
      <div className="flex flex-wrap items-start justify-between gap-3 border-b border-border-subtle/60 pb-3">
        <div>
          <span className="text-[11px] font-bold uppercase tracking-wider text-text-secondary flex items-center gap-1.5">
            <FlaskConical className="w-3.5 h-3.5 text-primary-400" />
            {recommendation.type || 'Disease Management'}
          </span>
          <h3 className="text-lg font-bold text-text-primary mt-1">
            {recommendation.active_ingredient || 'IPM / Crop Management'}
          </h3>
        </div>

        <span
          className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold border shadow-xs ${badge.badgeClass}`}
        >
          {badge.label}
        </span>
      </div>

      {/* Specifications / Dosage Grid */}
      {specs.length > 0 && (
        <dl className="grid grid-cols-1 sm:grid-cols-2 gap-3.5 py-4 text-sm border-b border-border-subtle/50">
          {specs.map((item) => (
            <div key={item.label} className="bg-surface-base/60 p-2.5 rounded-xl border border-border-subtle/40">
              <dt className="text-xs font-medium text-text-secondary mb-0.5">{item.label}</dt>
              <dd className="text-text-primary font-semibold text-sm">{item.value}</dd>
            </div>
          ))}
        </dl>
      )}

      {/* Authoritative Source Information */}
      <div className="pt-4 space-y-2">
        <div className="flex items-center gap-2 text-xs font-semibold text-text-secondary uppercase tracking-wider">
          <Building2 className="w-3.5 h-3.5 text-primary-400" />
          <span>Authoritative Source Provenance</span>
        </div>

        {source.organization && (
          <p className="text-sm font-bold text-text-primary">
            {source.organization}
            {source.source_type && (
              <span className="text-xs font-normal text-text-secondary ml-2">
                ({source.source_type})
              </span>
            )}
          </p>
        )}

        {source.document && (
          <p className="text-xs text-text-secondary flex items-start gap-1.5">
            <FileText className="w-3.5 h-3.5 text-primary-400 flex-shrink-0 mt-0.5" />
            <span>{source.document}</span>
          </p>
        )}

        {source.evidence_note && (
          <p className="text-xs text-text-secondary/90 italic bg-surface-base/40 p-2.5 rounded-xl border border-border-subtle/30">
            &ldquo;{source.evidence_note}&rdquo;
          </p>
        )}

        {source.url && (
          <div className="pt-2">
            <a
              href={source.url}
              target="_blank"
              rel="noreferrer"
              className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-xl bg-primary/10 hover:bg-primary/20 text-primary-400 border border-primary/20 text-xs font-bold transition-colors"
            >
              <span>View Official Reference</span>
              <ExternalLink className="w-3.5 h-3.5" />
            </a>
          </div>
        )}
      </div>
    </article>
  )
}
