'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { ChevronDown, KeyRound, User, LogOut, LayoutDashboard } from 'lucide-react'
import Link from 'next/link'
import { useAuth } from '@/contexts/AuthContext'
import { useI18n } from '@/contexts/I18nContext'

export default function UserMenu() {
  const { user, profile, signOut } = useAuth()
  const { t } = useI18n()
  const router = useRouter()
  const [open, setOpen] = useState(false)

  if (!user) return null

  const initials = (profile?.name || 'U')
    .split(' ')
    .map((w) => w[0])
    .slice(0, 2)
    .join('')
    .toUpperCase()

  const handleSignOut = async () => {
    await signOut()
    router.push('/')
  }

  return (
    <div className="relative">
      <button
        onClick={() => setOpen((o) => !o)}
        className="flex items-center gap-2 rounded-full pl-1 pr-2 py-1 bg-surface-card border border-border-subtle hover:border-primary-400/50 transition-colors"
      >
        <span className="w-8 h-8 rounded-full bg-primary-400 text-white text-xs font-bold flex items-center justify-center">
          {initials}
        </span>
        <span className="hidden md:block text-sm font-medium text-text-primary max-w-[8rem] truncate">
          {profile?.name || 'User'}
        </span>
        <ChevronDown className={`w-4 h-4 text-text-secondary transition-transform ${open ? 'rotate-180' : ''}`} />
      </button>

      {open && (
        <>
          <div className="fixed inset-0 z-40" onClick={() => setOpen(false)} />
          <div className="absolute right-0 mt-2 z-50 w-56 bg-surface-card border border-border-subtle rounded-xl shadow-xl overflow-hidden">
            <div className="px-4 py-3 border-b border-border-subtle">
              <p className="text-sm font-semibold text-text-primary truncate">{profile?.name}</p>
              <p className="text-xs text-text-secondary truncate">{profile?.email}</p>
            </div>
            <div className="py-1">
              <MenuItem
                href={profile?.role === 'admin' ? '/admin' : '/dashboard'}
                icon={LayoutDashboard}
                label={profile?.role === 'admin' ? 'Admin Dashboard' : t('nav.home')}
                onClick={() => setOpen(false)}
              />
              <MenuItem href="/profile" icon={User} label={t('nav.profile')} onClick={() => setOpen(false)} />
              <MenuItem href="/profile?tab=password" icon={KeyRound} label={t('nav.changePassword')} onClick={() => setOpen(false)} />
            </div>
            <div className="border-t border-border-subtle py-1">
              <button
                onClick={handleSignOut}
                className="w-full flex items-center gap-2.5 px-4 py-2.5 text-sm text-red-500 hover:bg-status-dangerBg/30 transition-colors"
              >
                <LogOut className="w-4 h-4" />
                {t('nav.signOut')}
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  )
}

function MenuItem({ href, icon: Icon, label, onClick }) {
  return (
    <Link
      href={href}
      onClick={onClick}
      className="flex items-center gap-2.5 px-4 py-2.5 text-sm text-text-primary hover:bg-surface-base transition-colors"
    >
      <Icon className="w-4 h-4 text-text-secondary" />
      {label}
    </Link>
  )
}