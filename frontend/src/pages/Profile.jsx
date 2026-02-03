import React, { useEffect, useState } from 'react'
import { api } from '../api'
import { useAuth } from '../state/AuthContext'

export default function Profile() {
  const [name, setName] = useState('')
  const [password, setPassword] = useState('')
  const [message, setMessage] = useState('')
  const { setUser, user } = useAuth()

  useEffect(() => {
    async function load() {
      const res = await api.get('/api/auth/me')
      setName(res.data.name || '')
    }
    load()
  }, [])

  const onSubmit = async (e) => {
    e.preventDefault()
    const payload = {}
    if (name) payload.name = name
    if (password) payload.password = password
    const res = await api.put('/api/auth/me', payload)
    setUser({ ...user, name: res.data.name })
    setMessage('Profile updated')
    setPassword('')
  }

  return (
    <div className="auth">
      <h2>Your profile</h2>
      <form onSubmit={onSubmit} className="card">
        <label>Name</label>
        <input value={name} onChange={e => setName(e.target.value)} />
        <label>Change password</label>
        <input type="password" value={password} onChange={e => setPassword(e.target.value)} />
        <button className="btn" type="submit">Save</button>
        {message && <div className="success">{message}</div>}
      </form>
    </div>
  )
}
