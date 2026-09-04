import axios from 'axios'

const API_URL =
  process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'

/**
 * Normalizes image URLs to prevent Mixed Content (HTTP on HTTPS) and resolve
 * localhost URLs to the production backend origin.
 */
export const getImageUrl = (url) => {
  if (!url) return '/placeholder-leaf.png'

  if (url.startsWith('data:') || url.startsWith('blob:')) {
    return url
  }

  const envApi = process.env.NEXT_PUBLIC_API_URL || ''
  let backendOrigin = ''
  if (envApi) {
    try {
      const parsed = new URL(envApi)
      backendOrigin = parsed.origin
    } catch {
      backendOrigin = envApi.replace(/\/api\/v1\/?$/, '')
    }
  }

  let formatted = url

  // If URL points to localhost/127.0.0.1 and we have a production backend configured
  if (formatted.includes('localhost:8000') || formatted.includes('127.0.0.1:8000')) {
    if (backendOrigin && !backendOrigin.includes('localhost') && !backendOrigin.includes('127.0.0.1')) {
      formatted = formatted.replace(/^http:\/\/(localhost|127\.0\.0\.1):8000/, backendOrigin)
    }
  }

  // If URL is relative
  if (formatted.startsWith('/uploads/')) {
    if (backendOrigin) {
      formatted = `${backendOrigin}${formatted}`
    }
  }

  // On HTTPS, upgrade http to https to avoid mixed-content blocking
  if (
    typeof window !== 'undefined' &&
    window.location.protocol === 'https:' &&
    formatted.startsWith('http://') &&
    !formatted.includes('localhost') &&
    !formatted.includes('127.0.0.1')
  ) {
    formatted = formatted.replace(/^http:\/\//i, 'https://')
  }

  return formatted
}

export const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Add auth token to requests
export const setAuthToken = (token) => {
  if (token) {
    api.defaults.headers.common['Authorization'] = `Bearer ${token}`
  } else {
    delete api.defaults.headers.common['Authorization']
  }
}

// API endpoints
export const authAPI = {
  register: (data, token) =>
    api.post('/auth/register', data, {
      headers: { Authorization: `Bearer ${token}` },
    }),
  me: (token) =>
    api.get('/auth/me', {
      headers: { Authorization: `Bearer ${token}` },
    }),
  changePassword: (data, token) =>
    api.post('/auth/change-password', data, {
      headers: { Authorization: `Bearer ${token}` },
    }),
  forgotPassword: (data) => api.post('/auth/forgot-password', data),
  resetPassword: (data) => api.post('/auth/reset-password', data),
}

// Misc / platform endpoints
export const miscAPI = {
  weather: (lat, lon) => api.get('/misc/weather', { params: { lat, lon } }),
  tips: () => api.get('/misc/tips'),
  contact: (data) => api.post('/misc/contact', data),
}

// AI Chatbot
export const chatAPI = {
  send: (data) => api.post('/chat', data),
}

export const predictionsAPI = {
  uploadImages: (formData, token) =>
    api.post('/predictions/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
        Authorization: `Bearer ${token}`,
      },
    }),
  analyze: (data, token) =>
    api.post('/predictions/analyze', data, {
      headers: { Authorization: `Bearer ${token}` },
    }),
  getAll: (params, token) =>
    api.get('/predictions', {
      params,
      headers: { Authorization: `Bearer ${token}` },
    }),
  getById: (id, token) =>
    api.get(`/predictions/${id}`, {
      headers: { Authorization: `Bearer ${token}` },
    }),
  downloadReport: (id, token) =>
    api.get(`/predictions/${id}/report`, {
      headers: { Authorization: `Bearer ${token}` },
      responseType: 'blob',
    }),
  downloadBatchReport: (data, token) =>
    api.post('/predictions/report/batch', data, {
      headers: { Authorization: `Bearer ${token}` },
      responseType: 'blob',
    }),
  deleteById: (id, token) =>
    api.delete(`/predictions/${id}`, {
      headers: { Authorization: `Bearer ${token}` },
    }),
  clearAll: (token) =>
    api.delete('/predictions/clear', {
      headers: { Authorization: `Bearer ${token}` },
    }),
}

export const adminAPI = {
  getDiseases: (token) =>
    api.get('/admin/diseases', {
      headers: { Authorization: `Bearer ${token}` },
    }),
  createDisease: (data, token) =>
    api.post('/admin/diseases', data, {
      headers: { Authorization: `Bearer ${token}` },
    }),
  updateDisease: (id, data, token) =>
    api.put(`/admin/diseases/${id}`, data, {
      headers: { Authorization: `Bearer ${token}` },
    }),
  deleteDisease: (id, token) =>
    api.delete(`/admin/diseases/${id}`, {
      headers: { Authorization: `Bearer ${token}` },
    }),
  getPesticides: (token) =>
    api.get('/admin/pesticides', {
      headers: { Authorization: `Bearer ${token}` },
    }),
  getAnalytics: (token) =>
    api.get('/admin/analytics', {
      headers: { Authorization: `Bearer ${token}` },
    }),
  getAllUsers: (token) =>
    api.get('/admin/users', {
      headers: { Authorization: `Bearer ${token}` },
    }),
  getAllPredictions: (token) =>
    api.get('/admin/predictions', {
      headers: { Authorization: `Bearer ${token}` },
    }),
  deletePrediction: (id, token) =>
    api.delete(`/admin/predictions/${id}`, {
      headers: { Authorization: `Bearer ${token}` },
    }),
  getContactMessages: (token) =>
    api.get('/admin/contact-messages', {
      headers: { Authorization: `Bearer ${token}` },
    }),
}

export default api
