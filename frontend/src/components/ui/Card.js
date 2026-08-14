export default function Card({
  children,
  className = '',
  hover = false,
  padded = true,
}) {
  return (
    <div
      className={`bg-surface-card rounded-2xl border border-border-subtle ${
        hover
          ? 'hover:border-primary-400/60 hover:-translate-y-1 transition-all duration-300'
          : ''
      } ${padded ? 'p-6' : ''} ${className}`}
    >
      {children}
    </div>
  )
}