import axios from 'axios'
import { useAuth } from './state/AuthContext'

const baseURL = import.meta.env.VITE_API_URL || 'http://localhost:5000'

export const api = axios.create({ baseURL })

export function setAuthToken(token) {
  if (token) {
    api.defaults.headers.common['Authorization'] = `Bearer ${token}`
  } else {
    delete api.defaults.headers.common['Authorization']
  }
}

// Initialize from localStorage if present
const saved = localStorage.getItem('token')
if (saved) setAuthToken(saved)
