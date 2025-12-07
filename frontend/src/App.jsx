import React, { useEffect, useState } from 'react'
import axios from 'axios'
import InvoiceList from './components/InvoiceList'
import UploadForm from './components/UploadForm'
import NotReceivedReport from './components/NotReceivedReport'

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'

export default function App() {
  const [invoices, setInvoices] = useState([])
  const [loading, setLoading] = useState(false)

  const refresh = async () => {
    setLoading(true)
    try {
      const { data } = await axios.get(`${API_BASE}/invoices`)
      setInvoices(data)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    refresh()
  }, [])

  const onUploaded = () => refresh()

  return (
    <div className="app">
      <header className="hero">
        <h1>Invoice Intake</h1>
        <p>Burnt orange, royal purple, and cappuccino mocha inspired controls.</p>
      </header>
      <main>
        <UploadForm apiBase={API_BASE} onUploaded={onUploaded} />
        <section>
          <h2>Parsed Invoices</h2>
          {loading ? <p>Loading…</p> : <InvoiceList invoices={invoices} />}
        </section>
        <section>
          <h2>Not Received Yet</h2>
          <NotReceivedReport apiBase={API_BASE} />
        </section>
      </main>
    </div>
  )
}
