'use client'

import { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { MessageCircle, X, Send, Bot, User } from 'lucide-react'
import { chatAPI } from '@/lib/api'
import { useI18n } from '@/contexts/I18nContext'

export default function Chatbot() {
  const { t } = useI18n()
  const [open, setOpen] = useState(false)
  const [messages, setMessages] = useState([
    { role: 'bot', text: 'Hi! I’m AgriBot 🌱. Ask me about tomato diseases, crop care, or treatments.' },
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  const handleSend = async () => {
    const text = input.trim()
    if (!text || loading) return
    setInput('')
    const history = messages
      .filter((m) => m.role !== 'bot' || m.text !== messages[0].text)
      .map((m) => ({ role: m.role === 'bot' ? 'assistant' : 'user', content: m.text }))
    const userMsg = { role: 'user', text }
    setMessages((prev) => [...prev, userMsg])
    setLoading(true)
    try {
      const res = await chatAPI.send({ message: text, history })
      setMessages((prev) => [...prev, { role: 'bot', text: res.data.reply }])
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          role: 'bot',
          text:
            err.response?.data?.detail ||
            t('chat.unavailable'),
        },
      ])
    } finally {
      setLoading(false)
    }
  }

  return (
    <>
      {/* Toggle button */}
      <button
        onClick={() => setOpen((o) => !o)}
        aria-label="Open AI assistant"
        className="fixed bottom-5 right-5 z-50 w-14 h-14 rounded-full bg-primary-400 text-white shadow-lg shadow-primary-400/30 flex items-center justify-center hover:bg-primary-500 transition-transform hover:scale-105"
      >
        {open ? <X className="w-6 h-6" /> : <MessageCircle className="w-6 h-6" />}
      </button>

      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ opacity: 0, y: 30, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 30, scale: 0.95 }}
            transition={{ duration: 0.2 }}
            className="fixed bottom-24 right-5 z-50 w-[calc(100vw-2.5rem)] max-w-sm sm:max-w-md h-[30rem] max-h-[70vh] flex flex-col bg-surface-card border border-border-subtle rounded-2xl shadow-2xl overflow-hidden"
          >
            <div className="flex items-center gap-3 px-4 py-3 border-b border-border-subtle bg-primary text-white">
              <span className="w-9 h-9 rounded-full bg-white/20 flex items-center justify-center">
                <Bot className="w-5 h-5" />
              </span>
              <div>
                <p className="font-semibold leading-tight">{t('chat.title')}</p>
                <p className="text-xs text-white/80">Online</p>
              </div>
            </div>

            <div className="flex-1 overflow-y-auto p-4 space-y-3">
              {messages.map((m, i) => (
                <div key={i} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                  <div
                    className={`max-w-[80%] px-3.5 py-2.5 rounded-2xl text-sm leading-relaxed ${
                      m.role === 'user'
                        ? 'bg-primary-400 text-white rounded-br-sm'
                        : 'bg-surface-base text-text-primary border border-border-subtle rounded-bl-sm'
                    }`}
                  >
                    {m.text}
                  </div>
                </div>
              ))}
              {loading && (
                <div className="flex justify-start">
                  <div className="bg-surface-base border border-border-subtle rounded-2xl rounded-bl-sm px-4 py-3 flex gap-1.5">
                    <span className="w-2 h-2 rounded-full bg-primary-400 animate-bounce" />
                    <span className="w-2 h-2 rounded-full bg-primary-400 animate-bounce [animation-delay:120ms]" />
                    <span className="w-2 h-2 rounded-full bg-primary-400 animate-bounce [animation-delay:240ms]" />
                  </div>
                </div>
              )}
              <div ref={bottomRef} />
            </div>

            <div className="p-3 border-t border-border-subtle flex items-center gap-2">
              <input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                placeholder={t('chat.placeholder')}
                className="flex-1 bg-surface-base border border-border-subtle rounded-full px-4 py-2.5 text-sm text-text-primary focus:outline-none focus:ring-2 focus:ring-primary-400"
              />
              <button
                onClick={handleSend}
                disabled={!input.trim() || loading}
                className="w-10 h-10 rounded-full bg-primary-400 text-white flex items-center justify-center disabled:opacity-40 hover:bg-primary-500 transition-colors"
                aria-label="Send"
              >
                <Send className="w-4 h-4" />
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  )
}