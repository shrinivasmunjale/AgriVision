'use client'

import { useAuth } from '@/contexts/AuthContext'
import { useRouter } from 'next/navigation'
import { useEffect, useState } from 'react'
import { useQuery, useQueryClient, useMutation } from '@tanstack/react-query'
import { adminAPI, predictionsAPI, getImageUrl } from '@/lib/api'
import Layout from '@/components/Layout'
import { Users, Activity, TrendingUp, Database, Eye, User, Calendar, Mail, Phone, MapPin, Trash2 } from 'lucide-react'
import { motion } from 'framer-motion'
import Link from 'next/link'

export default function AdminPage() {
  const { user, loading, getAccessToken, profile } = useAuth()
  const router = useRouter()
  const [activeTab, setActiveTab] = useState('overview') // 'overview', 'users', 'predictions', 'messages'

  useEffect(() => {
    if (!loading && !user) {
      router.push('/auth/login')
    } else if (!loading && profile && profile.role !== 'admin') {
      router.push('/dashboard')
    }
  }, [user, loading, profile, router])

  const { data: analytics, isLoading: analyticsLoading } = useQuery({
    queryKey: ['admin-analytics'],
    queryFn: async () => {
      const token = await getAccessToken()
      const response = await adminAPI.getAnalytics(token)
      return response.data
    },
    enabled: !!user && profile?.role === 'admin',
  })

  const { data: usersData, isLoading: usersLoading } = useQuery({
    queryKey: ['admin-users'],
    queryFn: async () => {
      const token = await getAccessToken()
      const response = await adminAPI.getAllUsers(token)
      return response.data
    },
    enabled: !!user && profile?.role === 'admin' && activeTab === 'users',
  })

  const { data: predictionsData, isLoading: predictionsLoading } = useQuery({
    queryKey: ['admin-predictions'],
    queryFn: async () => {
      const token = await getAccessToken()
      const response = await adminAPI.getAllPredictions(token)
      return response.data
    },
    enabled: !!user && profile?.role === 'admin' && activeTab === 'predictions',
  })

  const queryClient = useQueryClient()
  const [deletingId, setDeletingId] = useState(null)

  const deletePredictionMutation = useMutation({
    mutationFn: async (id) => {
      const token = await getAccessToken()
      return adminAPI.deletePrediction(id, token)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-predictions'] })
      queryClient.invalidateQueries({ queryKey: ['admin-analytics'] })
      setDeletingId(null)
    },
    onError: () => {
      setDeletingId(null)
    },
  })

  const handleDeletePrediction = (id) => {
    if (
      window.confirm(
        'Are you sure you want to delete this prediction? This action cannot be undone.'
      )
    ) {
      setDeletingId(id)
      deletePredictionMutation.mutate(id)
    }
  }

  const { data: messagesData, isLoading: messagesLoading } = useQuery({
    queryKey: ['admin-messages'],
    queryFn: async () => {
      const token = await getAccessToken()
      const response = await adminAPI.getContactMessages(token)
      return response.data
    },
    enabled: !!user && profile?.role === 'admin' && activeTab === 'messages',
  })

  if (loading || !user || !profile || profile.role !== 'admin') {
    return (
      <Layout>
        <div className="flex items-center justify-center min-h-screen">
          <div className="w-16 h-16 border-4 border-primary-400 border-t-transparent rounded-full animate-spin"></div>
        </div>
      </Layout>
    )
  }

  return (
    <Layout>
      <div className="p-4 lg:p-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <h1 className="text-3xl font-bold text-text-primary mb-2">
            Admin Dashboard
          </h1>
          <p className="text-text-secondary mb-8">
            Platform analytics and management
          </p>

          {/* Tabs */}
          <div className="flex gap-2 mb-6 border-b border-border-subtle overflow-x-auto">
            <button
              onClick={() => setActiveTab('overview')}
              className={`px-4 py-2 font-medium transition-colors whitespace-nowrap ${
                activeTab === 'overview'
                  ? 'text-primary-400 border-b-2 border-primary-400'
                  : 'text-text-secondary hover:text-text-primary'
              }`}
            >
              Overview
            </button>
            <button
              onClick={() => setActiveTab('users')}
              className={`px-4 py-2 font-medium transition-colors whitespace-nowrap ${
                activeTab === 'users'
                  ? 'text-primary-400 border-b-2 border-primary-400'
                  : 'text-text-secondary hover:text-text-primary'
              }`}
            >
              All Users
            </button>
            <button
              onClick={() => setActiveTab('predictions')}
              className={`px-4 py-2 font-medium transition-colors whitespace-nowrap ${
                activeTab === 'predictions'
                  ? 'text-primary-400 border-b-2 border-primary-400'
                  : 'text-text-secondary hover:text-text-primary'
              }`}
            >
              All Predictions
            </button>
            <button
              onClick={() => setActiveTab('messages')}
              className={`px-4 py-2 font-medium transition-colors whitespace-nowrap ${
                activeTab === 'messages'
                  ? 'text-primary-400 border-b-2 border-primary-400'
                  : 'text-text-secondary hover:text-text-primary'
              }`}
            >
              Contact Messages
            </button>
          </div>

          {/* Overview Tab */}
          {activeTab === 'overview' && (
            <>
              {analyticsLoading ? (
                <div className="text-center py-12">
                  <div className="w-12 h-12 border-4 border-primary-400 border-t-transparent rounded-full animate-spin mx-auto"></div>
                </div>
              ) : analytics ? (
                <>
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
                    <motion.div
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: 0.1 }}
                      className="bg-surface-card rounded-2xl p-6 border border-border-subtle"
                    >
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="text-text-secondary text-sm mb-1">Total Users</p>
                          <p className="text-3xl font-bold text-text-primary">
                            {analytics.total_users}
                          </p>
                        </div>
                        <div className="w-12 h-12 bg-primary-400/20 rounded-xl flex items-center justify-center">
                          <Users className="w-6 h-6 text-primary-400" />
                        </div>
                      </div>
                    </motion.div>

                    <motion.div
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: 0.2 }}
                      className="bg-surface-card rounded-2xl p-6 border border-border-subtle"
                    >
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="text-text-secondary text-sm mb-1">Total Scans</p>
                          <p className="text-3xl font-bold text-text-primary">
                            {analytics.total_predictions}
                          </p>
                        </div>
                        <div className="w-12 h-12 bg-primary-400/20 rounded-xl flex items-center justify-center">
                          <Activity className="w-6 h-6 text-primary-400" />
                        </div>
                      </div>
                    </motion.div>

                    <motion.div
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: 0.3 }}
                      className="bg-surface-card rounded-2xl p-6 border border-border-subtle"
                    >
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="text-text-secondary text-sm mb-1">Avg Confidence</p>
                          <p className="text-3xl font-bold text-text-primary">
                            {analytics.average_confidence}%
                          </p>
                        </div>
                        <div className="w-12 h-12 bg-primary-400/20 rounded-xl flex items-center justify-center">
                          <TrendingUp className="w-6 h-6 text-primary-400" />
                        </div>
                      </div>
                    </motion.div>

                    <motion.div
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: 0.4 }}
                      className="bg-surface-card rounded-2xl p-6 border border-border-subtle"
                    >
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="text-text-secondary text-sm mb-1">Diseases</p>
                          <p className="text-3xl font-bold text-text-primary">
                            {analytics.disease_distribution?.length || 0}
                          </p>
                        </div>
                        <div className="w-12 h-12 bg-primary-400/20 rounded-xl flex items-center justify-center">
                          <Database className="w-6 h-6 text-primary-400" />
                        </div>
                      </div>
                    </motion.div>
                  </div>

                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.5 }}
                    className="bg-surface-card rounded-2xl p-6 border border-border-subtle mb-8"
                  >
                    <h2 className="text-xl font-bold text-text-primary mb-4">
                      Disease Distribution
                    </h2>
                    <div className="space-y-3">
                      {analytics.disease_distribution?.map((item, index) => {
                        const total = analytics.total_predictions
                        const percentage = total > 0 ? ((item.count / total) * 100).toFixed(1) : 0
                        return (
                          <div key={index}>
                            <div className="flex items-center justify-between mb-2">
                              <span className="text-text-primary">{item.disease}</span>
                              <span className="text-text-secondary text-sm">
                                {item.count} ({percentage}%)
                              </span>
                            </div>
                            <div className="w-full bg-surface-base rounded-full h-2">
                              <div
                                className="bg-primary-400 h-2 rounded-full"
                                style={{ width: `${percentage}%` }}
                              />
                            </div>
                          </div>
                        )
                      })}
                    </div>
                  </motion.div>

                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.6 }}
                    className="bg-surface-card rounded-2xl p-6 border border-border-subtle"
                  >
                    <h2 className="text-xl font-bold text-text-primary mb-4">
                      Recent Activity
                    </h2>
                    {analytics.recent_audits && analytics.recent_audits.length > 0 ? (
                      <div className="space-y-3">
                        {analytics.recent_audits.map((audit, index) => (
                          <div
                            key={index}
                            className="flex items-center justify-between p-3 bg-surface-base rounded-lg"
                          >
                            <div>
                              <p className="text-text-primary">
                                <span className="font-semibold">{audit.action}</span> {audit.entity}
                              </p>
                              <p className="text-text-secondary text-xs">
                                {new Date(audit.timestamp).toLocaleString()}
                              </p>
                            </div>
                            <span className="text-text-secondary text-xs">
                              ID: {audit.entity_id}
                            </span>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <p className="text-text-secondary text-center py-4">No recent activity</p>
                    )}
                  </motion.div>
                </>
              ) : null}
            </>
          )}

          {/* Users Tab */}
          {activeTab === 'users' && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="bg-surface-card rounded-2xl p-6 border border-border-subtle"
            >
              <h2 className="text-xl font-bold text-text-primary mb-4">All Users</h2>
              {usersLoading ? (
                <div className="text-center py-12">
                  <div className="w-12 h-12 border-4 border-primary-400 border-t-transparent rounded-full animate-spin mx-auto"></div>
                </div>
              ) : usersData && usersData.length > 0 ? (
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b border-border-subtle">
                        <th className="text-left py-3 px-4 text-text-secondary font-medium text-sm">Name</th>
                        <th className="text-left py-3 px-4 text-text-secondary font-medium text-sm">Email</th>
                        <th className="text-left py-3 px-4 text-text-secondary font-medium text-sm">Role</th>
                        <th className="text-left py-3 px-4 text-text-secondary font-medium text-sm">Farm/Org</th>
                        <th className="text-left py-3 px-4 text-text-secondary font-medium text-sm">Phone</th>
                        <th className="text-left py-3 px-4 text-text-secondary font-medium text-sm">Joined</th>
                      </tr>
                    </thead>
                    <tbody>
                      {usersData.map((u) => (
                        <tr key={u.id} className="border-b border-border-subtle hover:bg-surface-base">
                          <td className="py-3 px-4">
                            <div className="flex items-center gap-2">
                              <div className="w-8 h-8 rounded-full bg-primary-400/20 flex items-center justify-center">
                                <User className="w-4 h-4 text-primary-400" />
                              </div>
                              <span className="text-text-primary font-medium">{u.name}</span>
                            </div>
                          </td>
                          <td className="py-3 px-4 text-text-primary">{u.email}</td>
                          <td className="py-3 px-4">
                            <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                              u.role === 'admin' ? 'bg-red-400/20 text-red-400' :
                              u.role === 'expert' ? 'bg-blue-400/20 text-blue-400' :
                              'bg-green-400/20 text-green-400'
                            }`}>
                              {u.role}
                            </span>
                          </td>
                          <td className="py-3 px-4 text-text-secondary">{u.farm_name || '-'}</td>
                          <td className="py-3 px-4 text-text-secondary">{u.phone || '-'}</td>
                          <td className="py-3 px-4 text-text-secondary text-sm">
                            {new Date(u.created_at).toLocaleDateString()}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <p className="text-text-secondary text-center py-8">No users found</p>
              )}
            </motion.div>
          )}

          {/* Predictions Tab */}
          {activeTab === 'predictions' && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="bg-surface-card rounded-2xl p-6 border border-border-subtle"
            >
              <h2 className="text-xl font-bold text-text-primary mb-4">All Predictions</h2>
              {predictionsLoading ? (
                <div className="text-center py-12">
                  <div className="w-12 h-12 border-4 border-primary-400 border-t-transparent rounded-full animate-spin mx-auto"></div>
                </div>
              ) : predictionsData && predictionsData.length > 0 ? (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {predictionsData.map((pred) => (
                    <div key={pred.id} className="bg-surface-base rounded-xl p-4 border border-border-subtle hover:border-primary-400/50 transition-colors">
                      <div className="aspect-video rounded-lg overflow-hidden mb-3 bg-surface-card">
                        <img
                          src={getImageUrl(pred.image_url)}
                          alt="Prediction"
                          className="w-full h-full object-cover"
                          onError={(e) => {
                            e.target.src = '/placeholder-leaf.png'
                          }}
                        />
                      </div>
                      <div className="space-y-2">
                        <div className="flex items-center justify-between">
                          <span className="text-text-primary font-semibold text-sm">
                            {pred.disease_name || 'Unknown'}
                          </span>
                          <span className="text-primary-400 font-bold text-sm">
                            {(pred.confidence_score * 100).toFixed(1)}%
                          </span>
                        </div>
                        <div className="flex items-center gap-2 text-text-secondary text-xs">
                          <User className="w-3 h-3" />
                          <span>{pred.user_email || pred.user_id}</span>
                        </div>
                        <div className="flex items-center gap-2 text-text-secondary text-xs">
                          <Calendar className="w-3 h-3" />
                          <span>{new Date(pred.created_at).toLocaleDateString()}</span>
                        </div>
                        <Link
                          href={`/history/${pred.id}`}
                          className="flex items-center justify-center gap-2 w-full mt-3 px-3 py-2 bg-primary-400 text-white rounded-lg hover:bg-primary-500 transition-colors text-sm font-medium"
                        >
                          <Eye className="w-4 h-4" />
                          View Details
                        </Link>
                        <button
                          onClick={() => handleDeletePrediction(pred.id)}
                          disabled={deletingId === pred.id}
                          className="flex items-center justify-center gap-2 w-full mt-2 px-3 py-2 bg-red-400/10 text-red-400 border border-red-400/40 rounded-lg hover:bg-red-400/20 transition-colors text-sm font-medium disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                          {deletingId === pred.id ? (
                            <>
                              <span className="w-4 h-4 border-2 border-red-400 border-t-transparent rounded-full animate-spin"></span>
                              Deleting...
                            </>
                          ) : (
                            <>
                              <Trash2 className="w-4 h-4" />
                              Delete
                            </>
                          )}
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-text-secondary text-center py-8">No predictions found</p>
              )}
            </motion.div>
          )}

          {/* Contact Messages Tab */}
          {activeTab === 'messages' && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="bg-surface-card rounded-2xl p-6 border border-border-subtle"
            >
              <h2 className="text-xl font-bold text-text-primary mb-4">Farmer Contact Messages</h2>
              {messagesLoading ? (
                <div className="text-center py-12">
                  <div className="w-12 h-12 border-4 border-primary-400 border-t-transparent rounded-full animate-spin mx-auto"></div>
                </div>
              ) : messagesData && messagesData.length > 0 ? (
                <div className="space-y-4">
                  {messagesData.map((msg) => (
                    <div key={msg.id} className="bg-surface-base rounded-xl p-4 border border-border-subtle">
                      <div className="flex items-start justify-between mb-3">
                        <div className="flex items-center gap-3">
                          <div className="w-10 h-10 rounded-full bg-primary-400/20 flex items-center justify-center">
                            <User className="w-5 h-5 text-primary-400" />
                          </div>
                          <div>
                            <h3 className="text-text-primary font-semibold">{msg.name}</h3>
                            <div className="flex items-center gap-3 text-text-secondary text-sm">
                              <span className="flex items-center gap-1">
                                <Mail className="w-3 h-3" />
                                {msg.email}
                              </span>
                              {msg.phone && (
                                <span className="flex items-center gap-1">
                                  <Phone className="w-3 h-3" />
                                  {msg.phone}
                                </span>
                              )}
                            </div>
                          </div>
                        </div>
                        <span className="text-text-secondary text-xs">
                          {new Date(msg.created_at).toLocaleDateString('en-US', {
                            month: 'short',
                            day: 'numeric',
                            year: 'numeric',
                            hour: '2-digit',
                            minute: '2-digit',
                          })}
                        </span>
                      </div>
                      <div className="pl-13">
                        {msg.subject && (
                          <p className="mb-1 text-sm font-semibold text-text-primary">
                            {msg.subject}
                          </p>
                        )}
                        <p className="text-text-primary whitespace-pre-wrap">{msg.message}</p>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-text-secondary text-center py-8">No messages yet</p>
              )}
            </motion.div>
          )}
        </motion.div>
      </div>
    </Layout>
  )
}
