import React, { useEffect, useState } from 'react'
import axios from 'axios'

export default function NotReceivedReport({ apiBase }) {
  const [rows, setRows] = useState([])
  const [filter, setFilter] = useState('')

  useEffect(() => {
    axios.get(`${apiBase}/reports/not-received`).then(({ data }) => setRows(data))
  }, [apiBase])

  const filtered = rows.filter((row) => row.part_number.toLowerCase().includes(filter.toLowerCase()))

  return (
    <div className="card">
      <div className="toolbar">
        <input placeholder="Filter by part" value={filter} onChange={(e) => setFilter(e.target.value)} />
      </div>
      <ul className="list">
        {filtered.map((row) => (
          <li key={row.part_number}>
            <span className="title">{row.part_number}</span>
            <span className="meta">{row.description}</span>
            <span className="badge warning">Not received</span>
          </li>
        ))}
        {filtered.length === 0 && <li className="muted">All caught up!</li>}
      </ul>
    </div>
  )
}
