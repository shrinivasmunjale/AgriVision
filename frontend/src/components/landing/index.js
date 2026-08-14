import Navbar from '@/components/ui/Navbar'
import Hero from '@/components/landing/Hero'
import Features from '@/components/landing/Features'
import HowItWorks from '@/components/landing/HowItWorks'
import StatsSection from '@/components/landing/StatsSection'
import CTA from '@/components/landing/CTA'
import LandingFooter from '@/components/landing/LandingFooter'

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-surface-base">
      <Navbar />
      <Hero />
      <Features />
      <HowItWorks />
      <StatsSection />
      <CTA />
      <LandingFooter />
    </div>
  )
}