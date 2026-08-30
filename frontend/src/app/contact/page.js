'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import { Mail, MessageSquare, Send, User, Tag } from 'lucide-react'
import Layout from '@/components/Layout'
import Button from '@/components/ui/Button'
import Card from '@/components/ui/Card'
import { miscAPI } from '@/lib/api'
import { useAuth } from '@/contexts/AuthContext'
import { useRouter } from 'next/navigation'
import { useEffect } from 'react'
import { useI18n } from '@/contexts/I18nContext'

export default function ContactPage() {
  const { profile, loading: authLoading } = useAuth()
  const router = useRouter()
  const { t } = useI18n()
  const [form, setForm] = useState({ name: '', email: '', subject: '', message: '' })
  const [submitting, setSubmitting] = useState(false)
  const [success, setSuccess] = useState('')
  const [error, setError] = useState('')

  useEffect(() => {
    if (!authLoading && profile?.role === 'admin') {
      router.push('/admin')
    }
  }, [profile, authLoading, router])

  if (!authLoading && profile?.role === 'admin') {
    return null
  }

  const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value })

  const handleSubmit = async (e) => {
    e.preventDefault()
    setSubmitting(true)
    setError('')
    setSuccess('')
    try {
      const res = await miscAPI.contact(form)
      setSuccess(t('contact.sentSuccess') || res.data.message || 'Message sent!')
      setForm({ name: '', email: '', subject: '', message: '' })
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to send message')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <Layout>
      <div className="p-4 lg:p-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="max-w-2xl mx-auto"
        >
          <div className="flex items-center gap-3 mb-2">
            <MessageSquare className="w-8 h-8 text-primary-400" />
            <h1 className="text-3xl font-bold text-text-primary">{t('contact.title')}</h1>
          </div>
          <p className="text-text-secondary mb-8">
            {t('contact.subtitle')}
          </p>

          <Card>
            {success && (
              <div className="mb-4 p-3 bg-status-successBg text-status-successText rounded-lg text-sm">{success}</div>
            )}
            {error && (
              <div className="mb-4 p-3 bg-status-dangerBg text-status-dangerText rounded-lg text-sm">{error}</div>
            )}

            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <FieldBox icon={User} label={t('contact.name')}>
                  <input
                    name="name"
                    value={form.name}
                    onChange={handleChange}
                    className="w-full pl-10 pr-3 py-2.5 bg-surface-base border border-border-subtle rounded-xl text-text-primary focus:outline-none focus:ring-2 focus:ring-primary-400"
                    placeholder="Your name"
                  />
                </FieldBox>
                <FieldBox icon={Mail} label={t('contact.email')}>
                  <input
                    name="email"
                    type="email"
                    required
                    value={form.email}
                    onChange={handleChange}
                    className="w-full pl-10 pr-3 py-2.5 bg-surface-base border border-border-subtle rounded-xl text-text-primary focus:outline-none focus:ring-2 focus:ring-primary-400"
                    placeholder="you@example.com"
                  />
                </FieldBox>
              </div>
              <FieldBox icon={Tag} label={t('contact.subject')}>
                <input
                  name="subject"
                  value={form.subject}
                  onChange={handleChange}
                  className="w-full pl-10 pr-3 py-2.5 bg-surface-base border border-border-subtle rounded-xl text-text-primary focus:outline-none focus:ring-2 focus:ring-primary-400"
                  placeholder="How can we help?"
                />
              </FieldBox>
              <FieldBox icon={MessageSquare} label={t('contact.message')}>
                <textarea
                  name="message"
                  required
                  rows={5}
                  value={form.message}
                  onChange={handleChange}
                  className="w-full pl-10 pr-3 py-2.5 bg-surface-base border border-border-subtle rounded-xl text-text-primary focus:outline-none focus:ring-2 focus:ring-primary-400"
                  placeholder="Write your message..."
                />
              </FieldBox>
              <Button type="submit" loading={submitting} className="w-full">
                <Send className="w-4 h-4" /> {t('contact.send')}
              </Button>
            </form>
          </Card>
        </motion.div>
      </div>
    </Layout>
  )
}


function FieldBox({ icon: Icon, label, children }) {
  return (
    <div>
      <label className="block text-sm font-medium text-text-secondary mb-2">{label}</label>
      <div className="relative">
        <Icon className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-text-secondary" />
        {children}
      </div>
    </div>
  )
}