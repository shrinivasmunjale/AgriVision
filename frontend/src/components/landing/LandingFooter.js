'use client'

import Container from '@/components/ui/Container'
import ThemeToggle from '@/components/ui/ThemeToggle'
import Badge from '@/components/ui/Badge'

export default function LandingFooter() {
  const links = [
    { label: 'Features', href: '/#features' },
    { label: 'Farming Tips', href: '/tips' },
    { label: 'FAQ', href: '/faq' },
    { label: 'Contact', href: '/contact' },
  ]
  return (
    <footer className="border-t border-border-subtle py-10">
      <Container className="flex flex-col sm:flex-row items-center justify-between gap-6">
        <div className="flex flex-col items-center sm:items-start gap-2">
          <p className="text-text-secondary text-sm">
            © {new Date().getFullYear()} AgriVision AI. Built for smarter farming.
          </p>
          <nav className="flex flex-wrap items-center justify-center sm:justify-start gap-4">
            {links.map((l) => (
              <a
                key={l.href}
                href={l.href}
                className="text-sm text-text-secondary hover:text-primary-400 transition-colors"
              >
                {l.label}
              </a>
            ))}
          </nav>
        </div>
        <div className="flex items-center gap-2 text-text-secondary">
          <ThemeToggle />
          <Badge tone="neutral">Beta</Badge>
        </div>
      </Container>
    </footer>
  )
}