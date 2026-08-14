import { Sprout } from 'lucide-react'
import Link from 'next/link'

export default function Logo({ className = '' }) {
  return (
    <Link href="/" className={`flex items-center gap-2 group ${className}`}>
      <span className="w-9 h-9 rounded-xl bg-primary-400/15 flex items-center justify-center group-hover:bg-primary-400/25 transition-colors">
        <Sprout className="w-5 h-5 text-primary-400" />
      </span>
      <span className="text-xl font-bold tracking-tight text-text-primary">
        AgriVision<span className="text-primary-400"> AI</span>
      </span>
    </Link>
  )
}