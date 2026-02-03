import React from 'react'
import { Routes, Route, Navigate, Link } from 'react-router-dom'
import Login from './pages/Login'
import Register from './pages/Register'
import Dashboard from './pages/Dashboard'
import Activities from './pages/Activities'
import Recommendations from './pages/Recommendations'
import Profile from './pages/Profile'
import { useAuth } from './state/AuthContext'

function Protected({ children }) {
  const { token } = useAuth()
  if (!token) return <Navigate to="/login" replace />
  return children
}

function Nav() {
  const { token, logout } = useAuth()
  return (
    <nav className="nav">
      <div className="brand">CarbonTrack</div>
      {token ? (
        <div className="links">
          <Link to="/">Dashboard</Link>
          <Link to="/activities">Activities</Link>
          <Link to="/recommendations">Recommendations</Link>
          <Link to="/profile">Profile</Link>
          <button onClick={logout} className="btn">Logout</button>
        </div>
      ) : (
        <div className="links">
          <Link to="/login">Login</Link>
          <Link to="/register">Register</Link>
        </div>
      )}
    </nav>
  )
}

export default function App() {
  return (
    <div>
      <Nav />
      <div className="container">
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/" element={<Protected><Dashboard /></Protected>} />
          <Route path="/activities" element={<Protected><Activities /></Protected>} />
          <Route path="/recommendations" element={<Protected><Recommendations /></Protected>} />
          <Route path="/profile" element={<Protected><Profile /></Protected>} />
        </Routes>
      </div>
    </div>
  )
}
