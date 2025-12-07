import React from 'react'

export default function InvoiceView({ invoice }) {
  const lines = invoice.lines || []
  const firstFiveParts = lines.slice(0, 5)
  const lastPage = invoice.pages?.reduce(
    (latest, page) => (latest === null || page.page_number > latest.page_number ? page : latest),
    null,
  )
  const lastPageSummary = lastPage?.text_content?.trim()

  return (
    <div className="invoice-view">
      <h3>Invoice #{invoice.invoice_number}</h3>
      <p className="meta">PO: {invoice.order_number}</p>
      <p className="meta">Date: {invoice.invoice_date || 'n/a'}</p>
      <p className="meta">Vendor: {invoice.vendor_name}</p>
      <p className="meta">Customer: {invoice.customer_name}</p>

      <div className="insight-grid">
        <div className="insight-card">
          <h4>Invoice Snapshot</h4>
          <dl className="data-grid">
            <div>
              <dt>Invoice #</dt>
              <dd>{invoice.invoice_number || '—'}</dd>
            </div>
            <div>
              <dt>PO #</dt>
              <dd>{invoice.order_number || '—'}</dd>
            </div>
            <div>
              <dt>Billing Period</dt>
              <dd>
                {invoice.billing_period_start && invoice.billing_period_end
                  ? `${invoice.billing_period_start} to ${invoice.billing_period_end}`
                  : '—'}
              </dd>
            </div>
            <div>
              <dt>Due Date</dt>
              <dd>{invoice.due_date || '—'}</dd>
            </div>
            <div>
              <dt>Currency</dt>
              <dd>{invoice.currency || '—'}</dd>
            </div>
            <div>
              <dt>Payment Terms</dt>
              <dd>{invoice.payment_terms || '—'}</dd>
            </div>
          </dl>
        </div>

        <div className="insight-card">
          <h4>First 5 Part #s</h4>
          {firstFiveParts.length === 0 ? (
            <p className="muted">No line items found.</p>
          ) : (
            <ol className="parts-list">
              {firstFiveParts.map((line) => (
                <li key={line.id || line.part_number}>
                  <div className="title">{line.part_number}</div>
                  <div className="meta">
                    Qty: {line.quantity ?? '—'} • Unit: {line.unit_cost ?? '—'}
                  </div>
                  {line.description && <div className="muted">{line.description}</div>}
                </li>
              ))}
            </ol>
          )}
        </div>

        <div className="insight-card summary-card">
          <h4>Last Page Summary</h4>
          {lastPageSummary ? (
            <div className="summary-block">
              <p className="muted">Page {lastPage?.page_number}</p>
              <p>{lastPageSummary}</p>
            </div>
          ) : (
            <p className="muted">No summary text available from the final page.</p>
          )}
        </div>
      </div>

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
          {lines.map((line) => (
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
