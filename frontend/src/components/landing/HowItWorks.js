'use client'

import { motion } from 'framer-motion'
import { Camera, ScanSearch, Leaf } from 'lucide-react'
import Container from '@/components/ui/Container'
import SectionHeading from '@/components/ui/SectionHeading'

const steps = [
  {
    icon: Camera,
    title: 'Capture',
    desc: 'Take a clear photo of the affected tomato leaf with good lighting.',
  },
  {
    icon: ScanSearch,
    title: 'Analyze',
    desc: 'Upload it and our machine learning model scans for signs of disease.',
  },
  {
    icon: Leaf,
    title: 'Get Guidance',
    desc: 'Receive treatments, recommendations, and a downloadable report instantly.',
  },
]

export default function HowItWorks() {
  return (
    <section
      id="how-it-works"
      className="py-20 lg:py-28 bg-surface-canvas border-y border-border-subtle"
    >
      <Container>
        <SectionHeading
          eyebrow="How it works"
          title="From photo to plan in three steps"
          subtitle="No complex setup. Just snap, upload, and get guidance."
        />
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {steps.map((s, i) => {
            const Icon = s.icon
            return (
              <motion.div
                key={s.title}
                initial={{ opacity: 0, y: 24 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.15, duration: 0.5 }}
                className="relative text-center"
              >
                <div className="w-16 h-16 mx-auto rounded-2xl bg-primary-400 text-white flex items-center justify-center relative">
                  <Icon className="w-8 h-8" />
                  <span className="absolute -top-2 -right-2 w-6 h-6 rounded-full bg-accent text-white text-xs font-bold flex items-center justify-center">
                    {i + 1}
                  </span>
                </div>
                <h3 className="mt-5 text-xl font-bold text-text-primary">{s.title}</h3>
                <p className="mt-2 text-text-secondary leading-relaxed">{s.desc}</p>
              </motion.div>
            )
          })}
        </div>
      </Container>
    </section>
  )
}