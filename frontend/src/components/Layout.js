'use client'

import { useAuth } from '@/contexts/AuthContext'
import { useRouter, usePathname } from 'next/navigation'
import { Home, Camera, History, Settings, LogOut, BarChart3, Sun, Moon, HelpCircle, Lightbulb, MessageCircle } from 'lucide-react'
import Link from 'next/link'
import { useTheme } from '@/contexts/ThemeContext'
import UserMenu from '@/components/UserMenu'
import LanguageToggle from '@/components/ui/LanguageToggle'
import Chatbot from '@/components/Chatbot'
import { useI18n } from '@/contexts/I18nContext'
import { useMemo } from 'react'

const pageTitles = {
  '/dashboard': 'Dashboard',
  '/scan': 'Scan Plant Health',
  '/history': 'History',
  '/profile': 'Profile',
  '/admin': 'Admin',
}

export default function Layout({ children }) {
  const { user, signOut, profile } = useAuth()
  const router = useRouter()
  const pathname = usePathname()
  const { theme, toggle } = useTheme()
  const { t } = useI18n()

  const title = useMemo(() => {
    if (pathname?.startsWith('/history/')) return 'Prediction Detail'
    return pageTitles[pathname] || 'AgriVision AI'
  }, [pathname])

  const handleSignOut = async () => {
    await signOut()
    router.push('/auth/login')
  }

  const isAdmin = profile?.role === 'admin'

  const navItems = [
    { icon: Home, label: 'Home', href: '/dashboard' },
    ...(isAdmin ? [] : [
      { icon: Camera, label: 'Scan', href: '/scan' },
      { icon: History, label: 'History', href: '/history' },
    ]),
    ...(isAdmin ? [{ icon: BarChart3, label: 'Admin', href: '/admin' }] : []),
    ...(isAdmin ? [] : [
      { icon: Lightbulb, label: 'Tips', href: '/tips' },
      { icon: HelpCircle, label: 'FAQ', href: '/faq' },
      { icon: MessageCircle, label: 'Contact', href: '/contact' },
    ]),
    { icon: Settings, label: 'Profile', href: '/profile' },
  ]

  return (
    <div className="min-h-screen bg-surface-base">
      {/* Desktop Sidebar */}
      <aside className="hidden lg:fixed lg:inset-y-0 lg:flex lg:w-64 lg:flex-col">
        <div className="flex flex-col flex-1 min-h-0 bg-surface-card border-r border-border-subtle">
          <div className="flex items-center h-16 flex-shrink-0 px-4 border-b border-border-subtle">
            <h1 className="text-xl font-bold text-primary-400">AgriVision AI</h1>
          </div>
          <nav className="flex-1 px-2 py-4 space-y-1">
            {navItems.map((item) => {
              const Icon = item.icon
              const isActive = pathname === item.href
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`flex items-center px-4 py-3 text-sm font-medium rounded-xl transition-colors ${
                    isActive
                      ? 'bg-primary-400 text-white'
                      : 'text-text-secondary hover:bg-surface-base hover:text-text-primary'
                  }`}
                >
                  <Icon className="w-5 h-5 mr-3" />
                  {item.label}
                </Link>
              )
            })}
          </nav>
          <div className="flex-shrink-0 p-4 border-t border-border-subtle space-y-1">
            <button
              onClick={toggle}
              className="flex items-center w-full px-4 py-3 text-sm font-medium text-text-secondary hover:text-text-primary hover:bg-surface-base rounded-xl transition-colors"
            >
              {theme === 'dark' ? <Sun className="w-5 h-5 mr-3" /> : <Moon className="w-5 h-5 mr-3" />}
              {theme === 'dark' ? 'Light Mode' : 'Dark Mode'}
            </button>
            <button
              onClick={handleSignOut}
              className="flex items-center w-full px-4 py-3 text-sm font-medium text-text-secondary hover:text-text-primary hover:bg-surface-base rounded-xl transition-colors"
            >
              <LogOut className="w-5 h-5 mr-3" />
              Sign Out
            </button>
          </div>
        </div>
      </aside>

      {/* Mobile Bottom Nav */}
      <nav className="lg:hidden fixed bottom-0 inset-x-0 bg-surface-card border-t border-border-subtle z-50">
        <div className="flex justify-around items-center h-16">
          {navItems.slice(0, 5).map((item) => {
            const Icon = item.icon
            const isActive = pathname === item.href
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`flex flex-col items-center justify-center flex-1 h-full ${
                  isActive ? 'text-primary-400' : 'text-text-secondary'
                }`}
              >
                <Icon className="w-6 h-6" />
                <span className="text-xs mt-1">{item.label}</span>
              </Link>
            )
          })}
        </div>
      </nav>

      {/* Main Content */}
      <main className="lg:pl-64 pb-20 lg:pb-0">
        {/* Sticky top header */}
        <header className="sticky top-0 z-30 bg-surface-base/80 backdrop-blur-xl border-b border-border-subtle px-4 lg:px-8 flex items-center justify-between h-16">
          <h1 className="text-lg font-bold text-text-primary truncate">{title}</h1>
          <div className="flex items-center gap-2">
            <LanguageToggle />
            <UserMenu />
          </div>
        </header>
        <div className="max-w-7xl mx-auto">{children}</div>
      </main>

      {/* Global floating AI chatbot */}
      <Chatbot />
    </div>
  )
}
