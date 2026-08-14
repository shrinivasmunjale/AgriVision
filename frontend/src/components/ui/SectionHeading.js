import { motion } from 'framer-motion'

export default function SectionHeading({
  eyebrow,
  title,
  subtitle,
  align = 'center',
}) {
  const alignCls =
    align === 'center' ? 'text-center mx-auto' : 'text-left max-w-2xl'
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      transition={{ duration: 0.5 }}
      className={`max-w-2xl mb-12 lg:mb-16 ${alignCls}`}
    >
      {eyebrow && (
        <span className="inline-block px-3 py-1 rounded-full bg-primary-400/10 text-primary-400 text-xs font-bold uppercase tracking-wider mb-4">
          {eyebrow}
        </span>
      )}
      <h2 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-text-primary leading-tight mb-4">
        {title}
      </h2>
      {subtitle && (
        <p className="text-text-secondary text-lg leading-relaxed">{subtitle}</p>
      )}
    </motion.div>
  )
}