import React, { useState } from 'react'
import InvoiceView from './InvoiceView'

export default function InvoiceList({ invoices }) {
  const [selected, setSelected] = useState(null)

  return (
    <div className="grid">
      <div className="card">
        <ul className="list">
          {invoices.map((inv) => (
            <li key={inv.id} onClick={() => setSelected(inv)} className={selected?.id === inv.id ? 'active' : ''}>
              <div className="title">Invoice #{inv.invoice_number || inv.id}</div>
              <div className="meta">Vendor: {inv.vendor_name || 'Unknown'}</div>
              <div className="meta">Total: {inv.total ?? 'n/a'}</div>
            </li>
          ))}
          {invoices.length === 0 && <li className="muted">No invoices parsed yet.</li>}
        </ul>
      </div>
      <div className="card">
        {selected ? <InvoiceView invoice={selected} /> : <p className="muted">Select an invoice to inspect details.</p>}
      </div>
    </div>
  )
}
