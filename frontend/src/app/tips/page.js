'use client'

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import { Lightbulb, RefreshCw } from 'lucide-react'
import Layout from '@/components/Layout'
import Card from '@/components/ui/Card'
import Badge from '@/components/ui/Badge'
import { miscAPI } from '@/lib/api'

export default function TipsPage() {
  const { data, isLoading } = useQuery({
    queryKey: ['tips'],
    queryFn: async () => {
      const response = await miscAPI.tips()
      return response.data.tips
    },
  })

  return (
    <Layout>
      <div className="p-4 lg:p-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="max-w-3xl mx-auto"
        >
          <div className="flex items-center gap-3 mb-2">
            <Lightbulb className="w-8 h-8 text-accent" />
            <h1 className="text-3xl font-bold text-text-primary">Farming Tips</h1>
          </div>
          <p className="text-text-secondary mb-8">
            Practical advice to keep your crops healthy and productive.
          </p>

          <Badge tone="accent" className="mb-4">
            Daily best practices
          </Badge>

          {isLoading ? (
            <div className="text-center py-12">
              <div className="w-12 h-12 border-4 border-primary-400 border-t-transparent rounded-full animate-spin mx-auto"></div>
            </div>
          ) : (
            <div className="space-y-3">
              {data?.map((tip, i) => (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, x: -10 }}
                  whileInView={{ opacity: 1, x: 0 }}
                  viewport={{ once: true }}
                  transition={{ delay: Math.min(i * 0.05, 0.4) }}
                >
                  <Card className="flex items-start gap-3 p-4">
                    <span className="w-8 h-8 rounded-full bg-primary-400/15 flex items-center justify-center flex-shrink-0">
                      <RefreshCw className="w-4 h-4 text-primary-400" />
                    </span>
                    <p className="text-text-primary leading-relaxed pt-1.5">{tip}</p>
                  </Card>
                </motion.div>
              ))}
            </div>
          )}
        </motion.div>
      </div>
    </Layout>
  )
}