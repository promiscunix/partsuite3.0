import React, { useEffect, useState } from 'react'
import axios from 'axios'
import InvoiceList from './components/InvoiceList'
import UploadForm from './components/UploadForm'
import NotReceivedReport from './components/NotReceivedReport'

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'

export default function App() {
  const [invoices, setInvoices] = useState([])
  const [loading, setLoading] = useState(false)
  const [view, setView] = useState('home')

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

  const renderHome = () => (
    <section className="card landing">
      <div className="landing-content">
        <div>
          <h2>Welcome to your invoice workspace</h2>
          <p className="muted">
            Start with a quick action below. You can scan new invoices when PDFs arrive or review items that
            have already been parsed.
          </p>
        </div>
        <div className="cta-buttons">
          <button className="primary" type="button" onClick={() => setView('scan')}>
            Scan Invoices
          </button>
          <button className="secondary" type="button" onClick={() => setView('review')}>
            Review Invoices
          </button>
        </div>
        <ul className="list small">
          <li className="muted">• "Scan" uploads PDFs so the parser can extract vendor, totals, and lines.</li>
          <li className="muted">• "Review" lets you inspect parsed invoices and track not-yet-received ones.</li>
        </ul>
      </div>
    </section>
  )

  return (
    <div className="app">
      <header className="hero">
        <div className="hero-top">
          <div>
            <h1>Invoice Intake</h1>
            <p>Burnt orange, royal purple, and cappuccino mocha inspired controls.</p>
          </div>
          <div className="hero-actions">
            <button
              className={`pill ${view === 'home' ? 'active' : ''}`}
              type="button"
              onClick={() => setView('home')}
            >
              Home
            </button>
            <button
              className={`pill ${view === 'scan' ? 'active' : ''}`}
              type="button"
              onClick={() => setView('scan')}
            >
              Scan Invoices
            </button>
            <button
              className={`pill ${view === 'review' ? 'active' : ''}`}
              type="button"
              onClick={() => setView('review')}
            >
              Review Invoices
            </button>
          </div>
        </div>
      </header>
      <main>
        {view === 'home' && renderHome()}
        {view === 'scan' && <UploadForm apiBase={API_BASE} onUploaded={onUploaded} />}
        {view === 'review' && (
          <>
            <section className="card">
              <div className="section-header">
                <h2>Parsed Invoices</h2>
                <button className="secondary" type="button" onClick={refresh} disabled={loading}>
                  {loading ? 'Refreshing…' : 'Refresh'}
                </button>
              </div>
              {loading ? <p>Loading…</p> : <InvoiceList invoices={invoices} />}
            </section>
            <section className="card">
              <h2>Not Received Yet</h2>
              <NotReceivedReport apiBase={API_BASE} />
            </section>
          </>
        )}
      </main>
    </div>
  )
}
