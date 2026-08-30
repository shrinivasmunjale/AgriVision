'use client'

import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { ChevronDown, HelpCircle } from 'lucide-react'
import Layout from '@/components/Layout'
import Card from '@/components/ui/Card'

const faqs = [
  {
    q: 'What is AgriVision AI?',
    a: 'AgriVision AI is an AI-powered platform that detects tomato leaf diseases from photos and provides treatment recommendations, confidence scores, and downloadable PDF reports.',
  },
  {
    q: 'How do I scan my crop?',
    a: 'Go to the Scan page, drag and drop (or capture) a clear photo of the leaf, then click "Analyze Plant Health". Our model returns the diagnosis with a confidence score and recommendations.',
  },
  {
    q: 'Is my scan data safe?',
    a: 'Yes. All accounts are protected with secure JWT authentication, and your scan history is only accessible to your account.',
  },
  {
    q: 'Which crops are supported?',
    a: 'Currently the model is trained for tomato leaf diseases, including healthy leaves and several common diseases. More crops are planned.',
  },
  {
    q: 'How accurate is the model?',
    a: 'The model is based on EfficientNetB0 and generally reports high-confidence results. Always pair a diagnosis with advice from an agricultural expert before applying treatments.',
  },
  {
    q: 'Can I download my reports?',
    a: 'Yes. Every scan is saved to your history, and you can download a professional PDF report from the prediction detail page.',
  },
]

import { useAuth } from '@/contexts/AuthContext'
import { useRouter } from 'next/navigation'
import { useEffect } from 'react'

export default function FaqPage() {
  const { profile, loading } = useAuth()
  const router = useRouter()
  const [open, setOpen] = useState(0)

  useEffect(() => {
    if (!loading && profile?.role === 'admin') {
      router.push('/admin')
    }
  }, [profile, loading, router])

  if (!loading && profile?.role === 'admin') {
    return null
  }

  return (
    <Layout>
      <div className="p-4 lg:p-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="max-w-3xl mx-auto"
        >
          <div className="flex items-center gap-3 mb-2">
            <HelpCircle className="w-8 h-8 text-primary-400" />
            <h1 className="text-3xl font-bold text-text-primary">Frequently Asked Questions</h1>
          </div>
          <p className="text-text-secondary mb-8">
            Answers to the questions we hear most often.
          </p>

          <div className="space-y-3">
            {faqs.map((f, i) => {
              const isOpen = open === i
              return (
                <Card key={i} padded={false} className="overflow-hidden">
                  <button
                    onClick={() => setOpen(isOpen ? -1 : i)}
                    className="w-full flex items-center justify-between gap-4 px-5 py-4 text-left"
                  >
                    <span className="font-semibold text-text-primary">{f.q}</span>
                    <ChevronDown
                      className={`w-5 h-5 text-text-secondary flex-shrink-0 transition-transform ${
                        isOpen ? 'rotate-180' : ''
                      }`}
                    />
                  </button>
                  <AnimatePresence initial={false}>
                    {isOpen && (
                      <motion.div
                        initial={{ height: 0, opacity: 0 }}
                        animate={{ height: 'auto', opacity: 1 }}
                        exit={{ height: 0, opacity: 0 }}
                        transition={{ duration: 0.2 }}
                        className="overflow-hidden"
                      >
                        <p className="px-5 pb-4 text-text-secondary leading-relaxed">{f.a}</p>
                      </motion.div>
                    )}
                  </AnimatePresence>
                </Card>
              )
            })}
          </div>
        </motion.div>
      </div>
    </Layout>
  )
}