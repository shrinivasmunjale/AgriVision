'use client'

import { motion } from 'framer-motion'
import { ArrowRight, Camera, ChevronRight, Leaf } from 'lucide-react'
import Container from '@/components/ui/Container'
import Button from '@/components/ui/Button'
import Card from '@/components/ui/Card'
import Badge from '@/components/ui/Badge'
import { useAuth } from '@/contexts/AuthContext'

export default function Hero() {
  const { user, profile, loading } = useAuth()
  const isAdmin = profile?.role === 'admin'

  return (
    <section className="relative overflow-hidden">
      <div
        aria-hidden
        className="absolute inset-0 bg-[radial-gradient(60rem_40rem_at_70%_-10%,rgba(52,166,95,0.18),transparent)]"
      />
      <Container className="relative pt-20 pb-16 lg:pt-28 lg:pb-24 text-center">
        <motion.div
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <Badge tone="green" dot>
            Powered by machine learning
          </Badge>
          <h1 className="mt-6 text-4xl sm:text-6xl lg:text-7xl font-bold tracking-tight text-text-primary leading-[1.05] text-balance">
            Detect crop diseases{' '}
            <span className="text-primary-400">before they spread</span>
          </h1>
          <p className="mt-6 max-w-2xl mx-auto text-lg sm:text-xl text-text-secondary">
            AgriVision AI transforms a simple leaf photo into instant, actionable
            insights — protecting your harvest with smart treatment
            recommendations.
          </p>
          <div className="mt-10 flex flex-col sm:flex-row items-center justify-center gap-4">
            {!loading && user ? (
              <Button href={isAdmin ? '/admin' : '/scan'} size="lg">
                {isAdmin ? 'Admin Dashboard' : 'Scan Your Crops'} <ArrowRight className="w-5 h-5" />
              </Button>
            ) : (
              <Button href="/auth/register" size="lg">
                Start Free Scan <ArrowRight className="w-5 h-5" />
              </Button>
            )}
            {!user && (
              <Button href="/auth/login" variant="secondary" size="lg">
                Sign in
              </Button>
            )}
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.25, duration: 0.6 }}
          className="mt-16 mx-auto max-w-3xl"
        >
          <Card padded={false} className="overflow-hidden shadow-2xl shadow-black/30">
            <div className="flex items-center justify-between px-5 py-3 border-b border-border-subtle bg-surface-card">
              <div className="flex gap-1.5">
                <span className="w-3 h-3 rounded-full bg-status-dangerText/60" />
                <span className="w-3 h-3 rounded-full bg-accent/70" />
                <span className="w-3 h-3 rounded-full bg-primary-400/70" />
              </div>
              <span className="text-xs text-text-secondary">Scan result</span>
            </div>
            <div className="p-6 grid grid-cols-1 sm:grid-cols-2 gap-6 text-left">
              <div className="bg-surface-base rounded-xl p-4 flex flex-col justify-center">
                <div className="w-full aspect-square rounded-lg bg-gradient-to-br from-primary-400/25 to-primary-600/25 flex items-center justify-center">
                  <Leaf className="w-16 h-16 text-primary-400" />
                </div>
              </div>
              <div className="flex flex-col justify-center gap-4">
                <div>
                  <p className="text-text-secondary text-sm mb-1">Detected</p>
                  <p className="text-2xl font-bold text-text-primary">
                    Septoria leaf spot
                  </p>
                </div>
                <div className="space-y-3">
                  <div>
                    <div className="flex justify-between text-sm mb-1">
                      <span className="text-text-secondary">Confidence</span>
                      <span className="font-semibold text-primary-400">94%</span>
                    </div>
                    <div className="h-2 bg-surface-base rounded-full overflow-hidden">
                      <div className="h-full w-[94%] bg-primary-400 rounded-full" />
                    </div>
                  </div>
                  <Badge tone="danger">Treatment recommended</Badge>
                </div>
                <Button href="/scan" size="sm" variant="secondary">
                  Try it yourself <ChevronRight className="w-4 h-4" />
                </Button>
              </div>
            </div>
          </Card>
        </motion.div>
      </Container>
    </section>
  )
}