'use client'

import { motion } from 'framer-motion'
import Container from '@/components/ui/Container'
import Button from '@/components/ui/Button'
import { useAuth } from '@/contexts/AuthContext'

export default function CTA() {
  const { user } = useAuth()

  return (
    <section className="pb-20 lg:pb-28">
      <Container>
        <motion.div
          initial={{ opacity: 0, y: 24 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="relative overflow-hidden rounded-3xl bg-primary text-white p-10 lg:p-16 text-center"
        >
          <div
            aria-hidden
            className="absolute inset-0 bg-[radial-gradient(30rem_20rem_at_50%_-20%,rgba(162,244,200,0.25),transparent)]"
          />
          <div className="relative">
            <h2 className="text-3xl sm:text-4xl lg:text-5xl font-bold leading-tight">
              Ready to protect your harvest?
            </h2>
            <p className="mt-4 max-w-xl mx-auto text-white/80 text-lg">
              Join hundreds of farmers using AI to catch disease early and grow
              with confidence.
            </p>
            <div className="mt-8 flex flex-col sm:flex-row items-center justify-center gap-4">
              <Button
                href={user ? '/scan' : '/auth/register'}
                variant="secondary"
                size="lg"
                className="!bg-white !text-primary hover:!bg-white/90"
              >
                Get Started Free
              </Button>
              {!user && (
                <Button
                  href="/auth/login"
                  size="lg"
                  variant="ghost"
                  className="!text-white hover:!bg-white/10"
                >
                  Sign in
                </Button>
              )}
            </div>
          </div>
        </motion.div>
      </Container>
    </section>
  )
}