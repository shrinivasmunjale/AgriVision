'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import { Menu, X, ArrowRight } from 'lucide-react'
import Link from 'next/link'
import Logo from '@/components/ui/Logo'
import Button from '@/components/ui/Button'
import ThemeToggle from '@/components/ui/ThemeToggle'
import { useAuth } from '@/contexts/AuthContext'

const navLinks = [
  { label: 'Features', href: '#features' },
  { label: 'How it works', href: '#how-it-works' },
  { label: 'Stats', href: '#stats' },
  { label: 'Tips', href: '/tips' },
  { label: 'FAQ', href: '/faq' },
  { label: 'Contact', href: '/contact' },
]

export default function Navbar() {
  const [open, setOpen] = useState(false)
  const { user, profile, loading } = useAuth()
  const isAdmin = profile?.role === 'admin'

  const activeNavLinks = isAdmin
    ? [
        { label: 'Features', href: '/#features' },
        { label: 'How it works', href: '/#how-it-works' },
        { label: 'Stats', href: '/#stats' },
      ]
    : navLinks

  return (
    <header className="sticky top-0 z-40 bg-surface-base/80 backdrop-blur-xl border-b border-border-subtle">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16 lg:h-20">
          <Logo />

          <nav className="hidden md:flex items-center gap-8">
            {activeNavLinks.map((link) => (
              <a
                key={link.href}
                href={link.href}
                className="text-sm font-medium text-text-secondary hover:text-primary-400 transition-colors"
              >
                {link.label}
              </a>
            ))}
          </nav>

          <div className="flex items-center gap-3">
            <ThemeToggle />
            {!loading &&
              (user ? (
                <Button href={isAdmin ? '/admin' : '/dashboard'} size="md">
                  {isAdmin ? 'Admin Dashboard' : 'Dashboard'} <ArrowRight className="w-4 h-4" />
                </Button>
              ) : (
                <>
                  <Button href="/auth/login" variant="ghost" size="md" className="hidden md:inline-flex">
                    Sign in
                  </Button>
                  <Button href="/auth/register" size="md">
                    Get Started
                  </Button>
                </>
              ))}
            <button
              onClick={() => setOpen((o) => !o)}
              className="md:hidden w-10 h-10 rounded-lg flex items-center justify-center text-text-primary bg-surface-card"
              aria-label="Toggle menu"
            >
              {open ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>
          </div>
        </div>
      </div>

      {open && (
        <motion.nav
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="md:hidden border-t border-border-subtle bg-surface-base px-4 py-4 space-y-2"
        >
          {activeNavLinks.map((link) => (
            <a
              key={link.href}
              href={link.href}
              onClick={() => setOpen(false)}
              className="block px-3 py-2.5 rounded-lg text-text-secondary hover:text-primary-400 hover:bg-surface-card transition-colors"
            >
              {link.label}
            </a>
          ))}
          {!user && !loading && (
            <Link
              href="/auth/register"
              onClick={() => setOpen(false)}
              className="flex items-center gap-2 px-3 py-2.5 rounded-lg text-primary-400 font-semibold mt-2"
            >
              Get Started <ArrowRight className="w-4 h-4" />
            </Link>
          )}
        </motion.nav>
      )}
    </header>
  )
}