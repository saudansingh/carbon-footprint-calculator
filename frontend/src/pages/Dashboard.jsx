import React, { useEffect, useState } from 'react'
import { api } from '../api'
import { Line, Pie, Bar } from 'react-chartjs-2'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  ArcElement,
  BarElement,
  Tooltip,
  Legend,
} from 'chart.js'

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, ArcElement, BarElement, Tooltip, Legend)

function format(n) { return Math.round((n || 0) * 100) / 100 }

export default function Dashboard() {
  const [summary, setSummary] = useState(null)
  const [trend, setTrend] = useState([])

  useEffect(() => {
    async function load() {
      const s = await api.get('/api/analytics/summary')
      setSummary(s.data)
      const t = await api.get('/api/analytics/trend')
      setTrend(t.data.items)
    }
    load()
  }, [])

  const lineData = {
    labels: trend.map(d => d.date),
    datasets: [
      { label: 'Total (kg)', data: trend.map(d => d.total_kg), borderColor: '#2563eb', backgroundColor: 'rgba(37,99,235,.2)' },
      { label: 'Transport', data: trend.map(d => d.transport), borderColor: '#f59e0b', backgroundColor: 'rgba(245,158,11,.2)' },
      { label: 'Energy', data: trend.map(d => d.energy), borderColor: '#10b981', backgroundColor: 'rgba(16,185,129,.2)' },
      { label: 'Food', data: trend.map(d => d.food), borderColor: '#ef4444', backgroundColor: 'rgba(239,68,68,.2)' },
    ]
  }

  const pieData = summary ? {
    labels: ['Transport', 'Energy', 'Food'],
    datasets: [{
      data: [summary.by_category.transport, summary.by_category.energy, summary.by_category.food],
      backgroundColor: ['#f59e0b', '#10b981', '#ef4444']
    }]
  } : null

  return (
    <div className="grid">
      <div className="card">
        <h3>Overview</h3>
        {summary && (
          <div className="stats">
            <div className="stat"><div className="stat-title">Total</div><div className="stat-value">{format(summary.total_kg)} kg</div></div>
            <div className="stat"><div className="stat-title">Transport</div><div className="stat-value">{format(summary.by_category.transport)} kg</div></div>
            <div className="stat"><div className="stat-title">Energy</div><div className="stat-value">{format(summary.by_category.energy)} kg</div></div>
            <div className="stat"><div className="stat-title">Food</div><div className="stat-value">{format(summary.by_category.food)} kg</div></div>
          </div>
        )}
      </div>

      <div className="card"><h3>Emissions over time</h3><Line data={lineData} /></div>
      <div className="card"><h3>Category breakdown</h3>{pieData && <Pie data={pieData} />}</div>
    </div>
  )
}
