const tones = {
  green: 'bg-primary-400/15 text-primary-400',
  success: 'bg-status-successBg text-status-successText',
  danger: 'bg-status-dangerBg text-status-dangerText',
  warning: 'bg-status-dangerBg text-status-dangerText',
  accent: 'bg-accent/20 text-accent',
  neutral: 'bg-surface-base text-text-secondary border border-border-subtle',
}

export default function Badge({
  children,
  tone = 'green',
  dot = false,
  className = '',
}) {
  return (
    <span
      className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold ${tones[tone]} ${className}`}
    >
      {dot && <span className="w-1.5 h-1.5 rounded-full bg-current" />}
      {children}
    </span>
  )
}