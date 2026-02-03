import React, { useEffect, useState } from 'react'
import { api } from '../api'

export default function Recommendations() {
  const [data, setData] = useState(null)

  useEffect(() => {
    async function load() {
      const res = await api.get('/api/recommendations')
      setData(res.data)
    }
    load()
  }, [])

  return (
    <div>
      <h2>Personalized recommendations</h2>
      {!data && <div className="card">Loading...</div>}
      {data && (
        <div className="grid">
          <div className="card">
            <h3>Summary (last {data.window_days} days)</h3>
            <ul>
              <li>Transport: {Math.round(data.summary.by_category.transport * 100) / 100} kg</li>
              <li>Energy: {Math.round(data.summary.by_category.energy * 100) / 100} kg</li>
              <li>Food: {Math.round(data.summary.by_category.food * 100) / 100} kg</li>
            </ul>
          </div>
          <div className="card">
            <h3>AI suggestions <span className="badge">{data.source}</span></h3>
            <ol>
              {data.items.map((it, idx) => (
                <li key={idx}>
                  <span className={`pill pill-${it.category}`}>{it.category}</span> {it.advice}
                </li>
              ))}
            </ol>
          </div>
        </div>
      )}
    </div>
  )
}
