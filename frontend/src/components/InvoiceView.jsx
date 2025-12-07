import React from 'react'

const formatCurrency = (value) => {
  if (value === null || value === undefined || Number.isNaN(Number(value))) return '—'
  return Number(value).toLocaleString(undefined, { style: 'currency', currency: 'USD' })
}

export default function InvoiceView({ invoice }) {
  const lines = invoice.lines || []
  const topLines = lines.slice(0, 5)
  const hasMore = lines.length > 5

  return (
    <div className="invoice-view">
      <div className="section-header">
        <div>
          <p className="meta">Invoice snapshot</p>
          <h3>Invoice #{invoice.invoice_number || invoice.id}</h3>
        </div>
        <div className="badge warning">{invoice.vendor_name || 'Unknown vendor'}</div>
      </div>

      <div className="info-grid">
        <div>
          <p className="meta">Invoice date</p>
          <p className="title">{invoice.invoice_date || 'n/a'}</p>
        </div>
        <div>
          <p className="meta">Supplier</p>
          <p className="title">{invoice.vendor_name || 'Not captured'}</p>
        </div>
        <div>
          <p className="meta">Customer</p>
          <p className="title">{invoice.customer_name || 'Not captured'}</p>
        </div>
        <div>
          <p className="meta">PO / Order #</p>
          <p className="title">{invoice.order_number || '—'}</p>
        </div>
        <div>
          <p className="meta">Due date</p>
          <p className="title">{invoice.due_date || '—'}</p>
        </div>
        <div>
          <p className="meta">Currency</p>
          <p className="title">{invoice.currency || 'USD'}</p>
        </div>
      </div>

      <div className="card subcard">
        <div className="section-header">
          <div>
            <p className="meta">Top part numbers</p>
            <h4>First {topLines.length} of {lines.length || 0} lines</h4>
          </div>
          {hasMore && <span className="muted">Showing first 5 lines</span>}
        </div>
        <table className="lines">
          <thead>
            <tr>
              <th>Part #</th>
              <th>Description</th>
              <th>Qty</th>
              <th>UOM</th>
              <th>Unit Cost</th>
              <th>Extended</th>
            </tr>
          </thead>
          <tbody>
            {topLines.map((line) => (
              <tr key={line.id || line.part_number}>
                <td>{line.part_number || '—'}</td>
                <td className="muted">{line.description || 'No description'}</td>
                <td>{line.quantity ?? '—'}</td>
                <td>{line.uom || '—'}</td>
                <td>{formatCurrency(line.unit_cost)}</td>
                <td>{formatCurrency(line.extended_cost)}</td>
              </tr>
            ))}
            {topLines.length === 0 && (
              <tr>
                <td colSpan="6" className="muted">
                  No line items were parsed from this invoice.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      <div className="card subcard">
        <div className="section-header">
          <div>
            <p className="meta">Invoice totals</p>
            <h4>Summary</h4>
          </div>
          <div className="muted">Parser confidence: {(invoice.parsing_confidence ?? 0).toFixed(0)}%</div>
        </div>
        <div className="summary">
          <div>Subtotal: {formatCurrency(invoice.subtotal)}</div>
          <div>Tax: {formatCurrency(invoice.tax)}</div>
          <div>Freight: {formatCurrency(invoice.freight)}</div>
          <div>Other charges: {formatCurrency(invoice.charges?.reduce((sum, c) => sum + (c.amount || 0), 0))}</div>
          <div className="total">Total: {formatCurrency(invoice.total)}</div>
          <div className="muted">Lines captured: {lines.length}</div>
        </div>
      </div>
    </div>
  )
}
