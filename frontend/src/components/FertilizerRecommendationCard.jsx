'use client'

import { Leaf, Calendar, ExternalLink, ShieldCheck, Building2, CheckCircle2, FileText, Info } from 'lucide-react'

export default function FertilizerRecommendationCard({ recommendation, className = '' }) {
  if (!recommendation) return null

  const nutrients = recommendation.nutrients || {}
  const schedule = recommendation.application_schedule || {}
  const source = recommendation.source || {}

  return (
    <article
      className={`rounded-2xl border border-border-subtle bg-surface-card p-6 shadow-sm transition-all hover:border-primary-400/40 ${className}`}
    >
      {/* Header */}
      <div className="flex flex-wrap items-start justify-between gap-4 border-b border-border-subtle/60 pb-4">
        <div>
          <span className="text-[11px] font-bold uppercase tracking-wider text-emerald-400 flex items-center gap-1.5">
            <Leaf className="w-3.5 h-3.5 text-emerald-400" />
            Fertilizer Advisory Reference
          </span>
          <h3 className="text-2xl font-bold text-text-primary mt-1">
            {recommendation.crop || 'Tomato'}
            {recommendation.variety_type && (
              <span className="text-primary-400 ml-2 font-semibold">({recommendation.variety_type})</span>
            )}
          </h3>
          <p className="text-xs text-text-secondary mt-0.5">
            Crop Stage: <span className="font-semibold text-text-primary">{recommendation.crop_stage || 'Transplanting'}</span>
          </p>
        </div>

        {/* Source Badge */}
        <div className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-full text-xs font-bold bg-blue-500/15 text-blue-300 border border-blue-500/40 shadow-xs">
          <ShieldCheck className="w-4 h-4 text-blue-400" />
          <span>✓ UNIVERSITY RESEARCH SOURCE</span>
        </div>
      </div>

      {/* Recommended Nutrients Grid */}
      <div className="my-5">
        <h4 className="text-xs font-bold uppercase tracking-wider text-text-secondary mb-3">
          Recommended Nutrients (per hectare)
        </h4>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          {nutrients.nitrogen && (
            <div className="bg-surface-base/80 p-3.5 rounded-xl border border-border-subtle/50 text-center">
              <span className="text-xs font-bold text-primary-400 block mb-0.5">Nitrogen (N)</span>
              <span className="text-xl font-extrabold text-text-primary">{nutrients.nitrogen.value}</span>
              <span className="text-[11px] text-text-secondary block mt-0.5">{nutrients.nitrogen.unit || 'kg/ha'}</span>
            </div>
          )}
          {nutrients.phosphorus && (
            <div className="bg-surface-base/80 p-3.5 rounded-xl border border-border-subtle/50 text-center">
              <span className="text-xs font-bold text-teal-400 block mb-0.5">Phosphorus (P₂O₅)</span>
              <span className="text-xl font-extrabold text-text-primary">{nutrients.phosphorus.value}</span>
              <span className="text-[11px] text-text-secondary block mt-0.5">{nutrients.phosphorus.unit || 'kg/ha'}</span>
            </div>
          )}
          {nutrients.potassium && (
            <div className="bg-surface-base/80 p-3.5 rounded-xl border border-border-subtle/50 text-center">
              <span className="text-xs font-bold text-amber-400 block mb-0.5">Potassium (K₂O)</span>
              <span className="text-xl font-extrabold text-text-primary">{nutrients.potassium.value}</span>
              <span className="text-[11px] text-text-secondary block mt-0.5">{nutrients.potassium.unit || 'kg/ha'}</span>
            </div>
          )}
          {nutrients.fym && (
            <div className="bg-surface-base/80 p-3.5 rounded-xl border border-border-subtle/50 text-center">
              <span className="text-xs font-bold text-emerald-400 block mb-0.5">Organic FYM</span>
              <span className="text-xl font-extrabold text-text-primary">{nutrients.fym.value}</span>
              <span className="text-[11px] text-text-secondary block mt-0.5">{nutrients.fym.unit || 'tonnes/ha'}</span>
            </div>
          )}
        </div>
      </div>

      {/* Application Schedule */}
      <div className="my-5 p-4 rounded-xl bg-surface-base/60 border border-border-subtle/50 space-y-3.5">
        <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-text-secondary">
          <Calendar className="w-4 h-4 text-primary-400" />
          <span>Application Schedule</span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {/* At transplanting */}
          {schedule.transplanting && (
            <div className="bg-surface-card/70 p-3 rounded-lg border border-border-subtle/40">
              <span className="text-xs font-bold text-emerald-400 block mb-2">At Transplanting (Basal):</span>
              <ul className="space-y-1.5 text-xs text-text-primary">
                {schedule.transplanting.map((step, idx) => (
                  <li key={idx} className="flex items-start gap-2">
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 flex-shrink-0 mt-0.5" />
                    <span>{step}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Later / split applications */}
          {schedule.later_applications && (
            <div className="bg-surface-card/70 p-3 rounded-lg border border-border-subtle/40">
              <span className="text-xs font-bold text-primary-400 block mb-2">Top-Dressing Splits:</span>
              <ul className="space-y-1.5 text-xs text-text-primary">
                {schedule.later_applications.map((step, idx) => (
                  <li key={idx} className="flex items-start gap-2">
                    <CheckCircle2 className="w-3.5 h-3.5 text-primary-400 flex-shrink-0 mt-0.5" />
                    <span>{step}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>

      {/* Source Provenance */}
      <div className="border-t border-border-subtle/60 pt-4 space-y-2">
        <div className="flex items-center gap-2 text-xs font-semibold text-text-secondary uppercase tracking-wider">
          <Building2 className="w-3.5 h-3.5 text-blue-400" />
          <span>Research Provenance</span>
        </div>

        {source.organization && (
          <p className="text-sm font-bold text-text-primary">
            {source.organization}
            {source.source_type && (
              <span className="text-xs font-normal text-text-secondary ml-2">({source.source_type})</span>
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
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-xl bg-blue-500/10 hover:bg-blue-500/20 text-blue-400 border border-blue-500/20 text-xs font-bold transition-colors"
            >
              <span>View Official Reference ↗</span>
              <ExternalLink className="w-3.5 h-3.5" />
            </a>
          </div>
        )}
      </div>

      {/* Disclaimer */}
      <div className="mt-4 pt-3 border-t border-border-subtle/50 text-[11px] text-text-secondary/80 flex items-start gap-2">
        <Info className="w-4 h-4 text-text-secondary flex-shrink-0 mt-0.5" />
        <p>
          <strong>Reference guidance:</strong> This recommendation is based on an MPKV research reference. Actual fertilizer requirements may vary according to soil condition, crop stage, variety, previous crop, irrigation and local agricultural guidance. Follow current agricultural recommendations and product instructions before application.
        </p>
      </div>
    </article>
  )
}
