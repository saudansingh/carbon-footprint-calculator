import React, { useEffect, useState } from 'react'
import { api } from '../api'

const TYPES = [
  { value: 'car', label: 'Car (petrol, km)' },
  { value: 'flight', label: 'Flight (short-haul, km)' },
  { value: 'bus', label: 'Bus (km)' },
  { value: 'train', label: 'Train (km)' },
  { value: 'electricity', label: 'Electricity (kWh)' },
  { value: 'beef_meal', label: 'Beef meal (qty)' },
  { value: 'vegetarian_meal', label: 'Vegetarian meal (qty)' },
]

function EmissionRow({ a, onDelete, onEdit }) {
  return (
    <tr>
      <td>{a.date}</td>
      <td>{a.type}</td>
      <td>{a.category}</td>
      <td>{a.data.distance_km || a.data.kwh || a.data.quantity}</td>
      <td>{a.emission_kg}</td>
      <td>
        <button className="btn btn-secondary" onClick={() => onEdit(a)}>Edit</button>
        <button className="btn btn-danger" onClick={() => onDelete(a.id)}>Delete</button>
      </td>
    </tr>
  )
}

export default function Activities() {
  const [items, setItems] = useState([])
  const [date, setDate] = useState('')
  const [type, setType] = useState('car')
  const [value, setValue] = useState('')
  const [error, setError] = useState('')
  const [editId, setEditId] = useState(null)

  const load = async () => {
    const res = await api.get('/api/activities?limit=200')
    setItems(res.data.items)
  }

  useEffect(() => { load() }, [])

  const onSubmit = async (e) => {
    e.preventDefault()
    setError('')
    try {
      const data = {}
      if (['car', 'bus', 'train', 'flight'].includes(type)) data.distance_km = parseFloat(value)
      else if (type === 'electricity') data.kwh = parseFloat(value)
      else data.quantity = parseFloat(value || '1')

      if (editId) {
        const res = await api.put(`/api/activities/${editId}`, { type, date, data })
        setEditId(null)
      } else {
        const res = await api.post('/api/activities', { type, date, data })
      }
      setDate(''); setValue(''); setType('car')
      await load()
    } catch (err) {
      setError(err?.response?.data?.error || 'Save failed')
    }
  }

  const onDelete = async (id) => {
    await api.delete(`/api/activities/${id}`)
    await load()
  }

  const onEdit = (a) => {
    setEditId(a.id)
    setDate(a.date)
    setType(a.type)
    setValue(a.data.distance_km || a.data.kwh || a.data.quantity || '')
  }

  return (
    <div>
      <h2>Activities</h2>
      <form className="card form-row" onSubmit={onSubmit}>
        <input type="date" value={date} onChange={e => setDate(e.target.value)} />
        <select value={type} onChange={e => setType(e.target.value)}>
          {TYPES.map(t => <option key={t.value} value={t.value}>{t.label}</option>)}
        </select>
        <input placeholder="Value" value={value} onChange={e => setValue(e.target.value)} />
        <button className="btn" type="submit">{editId ? 'Update' : 'Add'}</button>
      </form>
      {error && <div className="error">{error}</div>}

      <div className="card">
        <table className="table">
          <thead>
            <tr><th>Date</th><th>Type</th><th>Category</th><th>Value</th><th>Emission (kg)</th><th></th></tr>
          </thead>
          <tbody>
            {items.map(a => <EmissionRow key={a.id} a={a} onDelete={onDelete} onEdit={onEdit} />)}
          </tbody>
        </table>
      </div>
    </div>
  )
}
