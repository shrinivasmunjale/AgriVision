'use client'

import { motion } from 'framer-motion'
import {
  ScanSearch,
  FlaskConical,
  FileText,
  BarChart3,
  ShieldCheck,
  Sprout,
} from 'lucide-react'
import Container from '@/components/ui/Container'
import SectionHeading from '@/components/ui/SectionHeading'
import Card from '@/components/ui/Card'

const features = [
  {
    icon: ScanSearch,
    title: 'AI Disease Detection',
    desc: 'Upload a photo of your crop and our EfficientNet AI instantly identifies diseases with a confidence score.',
  },
  {
    icon: FlaskConical,
    title: 'Smart Treatment Plans',
    desc: 'Get personalized pesticide and fertilizer recommendations tailored to your specific diagnosis.',
  },
  {
    icon: FileText,
    title: 'PDF Diagnosis Reports',
    desc: 'Download professional, shareable PDF reports for your records, veterinarians, or consultants.',
  },
  {
    icon: BarChart3,
    title: 'Farm Analytics',
    desc: 'Track crop health trends over time with a personalized dashboard of your scan history.',
  },
  {
    icon: ShieldCheck,
    title: 'Expert Role Support',
    desc: 'Built for farmers, agricultural experts, and admins with role-based access and management.',
  },
  {
    icon: Sprout,
    title: 'Digital Crop Records',
    desc: 'Your complete scan history stays organized and searchable for smarter, data-driven decisions.',
  },
]

export default function Features() {
  return (
    <section id="features" className="py-20 lg:py-28">
      <Container>
        <SectionHeading
          eyebrow="Features"
          title="Everything you need to protect your crops"
          subtitle="A complete toolkit that turns a simple photo into confident farm decisions."
        />
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map((f, i) => {
            const Icon = f.icon
            return (
              <motion.div
                key={f.title}
                initial={{ opacity: 0, y: 24 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: (i % 3) * 0.1, duration: 0.5 }}
              >
                <Card hover className="h-full">
                  <div className="w-12 h-12 rounded-xl bg-primary-400/15 flex items-center justify-center mb-4">
                    <Icon className="w-6 h-6 text-primary-400" />
                  </div>
                  <h3 className="text-lg font-bold text-text-primary mb-2">
                    {f.title}
                  </h3>
                  <p className="text-text-secondary leading-relaxed">{f.desc}</p>
                </Card>
              </motion.div>
            )
          })}
        </div>
      </Container>
    </section>
  )
}