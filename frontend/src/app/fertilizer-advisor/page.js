'use client'

import Layout from '@/components/Layout'
import FertilizerAdvisor from '@/components/FertilizerAdvisor'
import { motion } from 'framer-motion'
import { Leaf, Info } from 'lucide-react'

export default function FertilizerAdvisorPage() {
  return (
    <Layout>
      <div className="p-4 lg:p-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="max-w-5xl mx-auto space-y-6"
        >
          {/* Page Header */}
          <div>
            <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-emerald-400 mb-1">
              <Leaf className="w-4 h-4" />
              <span>Crop Nutrition & Fertilizer Advisory</span>
            </div>
            <h1 className="text-3xl font-bold text-text-primary">
              Tomato Fertilizer Advisor
            </h1>
            <p className="text-sm text-text-secondary mt-1 max-w-2xl">
              Get scientifically validated fertilizer schedules from Mahatma Phule Krishi Vidyapeeth (MPKV), Rahuri. Designed for Indian farmers with no soil-test prerequisite.
            </p>
          </div>

          {/* Main Interactive Advisor Component */}
          <FertilizerAdvisor />
        </motion.div>
      </div>
    </Layout>
  )
}
