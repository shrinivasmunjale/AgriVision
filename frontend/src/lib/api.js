import axios from 'axios'

const API_URL =
  process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'

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
}

export default api
