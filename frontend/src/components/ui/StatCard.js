import { motion } from 'framer-motion'

export default function StatCard({
  label,
  value,
  icon: Icon,
  suffix = '',
  delay = 0,
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      transition={{ delay, duration: 0.4 }}
      className="bg-surface-card rounded-2xl p-6 border border-border-subtle"
    >
      <div className="flex items-center justify-between">
        <div>
          <p className="text-text-secondary text-sm mb-1">{label}</p>
          <p className="text-3xl font-bold text-text-primary">
            {value}
            {suffix && (
              <span className="text-lg font-semibold text-primary-400">
                {suffix}
              </span>
            )}
          </p>
        </div>
        {Icon && (
          <div className="w-12 h-12 bg-primary-400/15 rounded-xl flex items-center justify-center">
            <Icon className="w-6 h-6 text-primary-400" />
          </div>
        )}
      </div>
    </motion.div>
  )
}