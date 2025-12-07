import React from 'react'

export default function InvoiceView({ invoice }) {
  return (
    <div className="invoice-view">
      <h3>Invoice #{invoice.invoice_number}</h3>
      <p className="meta">PO: {invoice.order_number}</p>
      <p className="meta">Date: {invoice.invoice_date || 'n/a'}</p>
      <p className="meta">Vendor: {invoice.vendor_name}</p>
      <p className="meta">Customer: {invoice.customer_name}</p>

      <div className="summary">
        <div>Subtotal: {invoice.subtotal ?? '—'}</div>
        <div>Tax: {invoice.tax ?? '—'}</div>
        <div>Freight: {invoice.freight ?? '—'}</div>
        <div className="total">Total: {invoice.total ?? '—'}</div>
      </div>

      <h4>Lines</h4>
      <table className="lines">
        <thead>
          <tr>
            <th>Part</th>
            <th>Qty</th>
            <th>Unit</th>
            <th>Extended</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          {invoice.lines.map((line) => (
            <tr key={line.id || line.part_number}>
              <td>{line.part_number}</td>
              <td>{line.quantity}</td>
              <td>{line.unit_cost}</td>
              <td>{line.extended_cost}</td>
              <td>
                <label className="toggle">
                  <input type="checkbox" defaultChecked={line.received} />
                  <span>Received</span>
                </label>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      <h4>GL Allocations</h4>
      <ul className="list">
        {invoice.allocations.map((alloc) => (
          <li key={alloc.account_code}>
            {alloc.account_code}: {alloc.amount} {alloc.memo ? `- ${alloc.memo}` : ''}
          </li>
        ))}
        {invoice.allocations.length === 0 && <li className="muted">No allocations detected.</li>}
      </ul>
    </div>
  )
}
