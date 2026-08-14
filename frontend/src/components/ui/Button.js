'use client'

import Link from 'next/link'
import { Loader } from 'lucide-react'

const variants = {
  primary:
    'bg-primary-400 text-white hover:bg-primary-500 shadow-lg shadow-primary-400/20',
  secondary:
    'bg-surface-card text-text-primary border border-border-subtle hover:border-primary-400/50 hover:text-primary-400',
  outline:
    'border border-primary-400/40 text-primary-400 hover:bg-primary-400/10',
  ghost: 'text-text-secondary hover:text-text-primary hover:bg-surface-card',
  danger: 'bg-red-500 text-white hover:bg-red-600',
}

const sizes = {
  sm: 'px-3.5 py-2 text-sm',
  md: 'px-5 py-2.5 text-sm',
  lg: 'px-7 py-3.5 text-base',
}

export default function Button({
  children,
  variant = 'primary',
  size = 'md',
  href,
  loading = false,
  className = '',
  ...props
}) {
  const classes = `inline-flex items-center justify-center gap-2 rounded-full font-semibold transition-all duration-200 active:scale-[.98] disabled:opacity-50 disabled:cursor-not-allowed disabled:active:scale-100 ${variants[variant]} ${sizes[size]} ${className}`

  if (href) {
    return (
      <Link href={href} className={classes} {...props}>
        {children}
      </Link>
    )
  }

  return (
    <button className={classes} disabled={loading || props.disabled} {...props}>
      {loading && <Loader className="w-4 h-4 animate-spin" />}
      {children}
    </button>
  )
}