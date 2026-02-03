import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api, setAuthToken } from '../api'
import { useAuth } from '../state/AuthContext'

export default function Register() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [name, setName] = useState('')
  const [error, setError] = useState('')
  const navigate = useNavigate()
  const { login } = useAuth()

  const onSubmit = async (e) => {
    e.preventDefault()
    setError('')
    try {
      const res = await api.post('/api/auth/register', { email, password, name })
      login(res.data.token, res.data.user)
      setAuthToken(res.data.token)
      navigate('/')
    } catch (err) {
      setError(err?.response?.data?.error || 'Registration failed')
    }
  }

  return (
    <div className="auth">
      <h2>Create account</h2>
      <form onSubmit={onSubmit} className="card">
        <label>Name</label>
        <input value={name} onChange={e => setName(e.target.value)} placeholder="Your name" />
        <label>Email</label>
        <input value={email} onChange={e => setEmail(e.target.value)} placeholder="you@example.com" />
        <label>Password</label>
        <input type="password" value={password} onChange={e => setPassword(e.target.value)} />
        {error && <div className="error">{error}</div>}
        <button className="btn" type="submit">Register</button>
      </form>
    </div>
  )
}
