import React from 'react'

function formatCurrency(value, currency = 'USD') {
  if (value === null || value === undefined || value === '') return '—'
  const numeric = Number(value)
  if (Number.isNaN(numeric)) return value
  try {
    return new Intl.NumberFormat('en-US', { style: 'currency', currency }).format(numeric)
  } catch (error) {
    return numeric.toLocaleString()
  }
}

function formatDate(value) {
  if (!value) return '—'
  const parsed = new Date(value)
  if (Number.isNaN(parsed.getTime())) return value
  return parsed.toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' })
}

export default function InvoiceView({ invoice }) {
  const lines = invoice.lines || []
  const allocations = invoice.allocations || []
  const firstFiveParts = lines.slice(0, 5)
  const lastPage = invoice.pages?.reduce(
    (latest, page) => (latest === null || page.page_number > latest.page_number ? page : latest),
    null,
  )
  const lastPageSummary = lastPage?.text_content?.trim()
  const currency = invoice.currency || 'USD'

  const billingPeriod =
    invoice.billing_period_start && invoice.billing_period_end
      ? `${formatDate(invoice.billing_period_start)} to ${formatDate(invoice.billing_period_end)}`
      : '—'

  return (
    <div className="invoice-view">
      <div className="invoice-header card">
        <div>
          <p className="eyebrow">Invoice overview</p>
          <h2>Invoice #{invoice.invoice_number || 'Unspecified'}</h2>
          <p className="muted">
            {invoice.vendor_name || 'Unknown vendor'} → {invoice.customer_name || 'Unknown customer'}
          </p>
        </div>
        <div className="pill-row">
          <span className="pill subtle">PO {invoice.order_number || '—'}</span>
          <span className="pill subtle">Currency {invoice.currency || '—'}</span>
          <span className="pill subtle">Payment {invoice.payment_terms || '—'}</span>
        </div>
      </div>

      <div className="card info-grid">
        <div>
          <p className="label">Invoice date</p>
          <p className="value">{formatDate(invoice.invoice_date)}</p>
        </div>
        <div>
          <p className="label">Due date</p>
          <p className="value">{formatDate(invoice.due_date)}</p>
        </div>
        <div>
          <p className="label">Billing period</p>
          <p className="value">{billingPeriod}</p>
        </div>
        <div>
          <p className="label">Remit to</p>
          <p className="value">{invoice.vendor_name || '—'}</p>
        </div>
        <div>
          <p className="label">Bill to</p>
          <p className="value">{invoice.customer_name || '—'}</p>
        </div>
      </div>

      <div className="stat-grid">
        <div className="stat-card">
          <p className="label">Subtotal</p>
          <p className="stat-value">{formatCurrency(invoice.subtotal, currency)}</p>
        </div>
        <div className="stat-card">
          <p className="label">Tax</p>
          <p className="stat-value">{formatCurrency(invoice.tax, currency)}</p>
        </div>
        <div className="stat-card">
          <p className="label">Freight</p>
          <p className="stat-value">{formatCurrency(invoice.freight, currency)}</p>
        </div>
        <div className="stat-card emphasis">
          <p className="label">Total due</p>
          <p className="stat-value">{formatCurrency(invoice.total, currency)}</p>
        </div>
      </div>

      <div className="insight-grid">
        <div className="insight-card">
          <h4>First 5 part numbers</h4>
          {firstFiveParts.length === 0 ? (
            <p className="muted">No line items found.</p>
          ) : (
            <ol className="parts-list">
              {firstFiveParts.map((line) => (
                <li key={line.id || line.part_number}>
                  <div className="title">{line.part_number || 'Unknown part'}</div>
                  <div className="meta">
                    Qty: {line.quantity ?? '—'} • Unit: {formatCurrency(line.unit_cost, currency)}
                  </div>
                  {line.description && <div className="muted">{line.description}</div>}
                </li>
              ))}
            </ol>
          )}
        </div>

        <div className="insight-card summary-card">
          <h4>Last page summary</h4>
          {lastPageSummary ? (
            <div className="summary-block">
              <p className="muted">Page {lastPage?.page_number}</p>
              <p>{lastPageSummary}</p>
            </div>
          ) : (
            <p className="muted">No summary text available from the final page.</p>
          )}
        </div>

        <div className="insight-card">
          <h4>Snapshot</h4>
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
              <dt>Billing period</dt>
              <dd>{billingPeriod}</dd>
            </div>
            <div>
              <dt>Due date</dt>
              <dd>{formatDate(invoice.due_date)}</dd>
            </div>
            <div>
              <dt>Currency</dt>
              <dd>{invoice.currency || '—'}</dd>
            </div>
            <div>
              <dt>Payment terms</dt>
              <dd>{invoice.payment_terms || '—'}</dd>
            </div>
          </dl>
        </div>
      </div>

      <div className="card">
        <div className="section-header">
          <h4>Line items</h4>
          <p className="muted">Showing {lines.length} line{lines.length === 1 ? '' : 's'}</p>
        </div>
        {lines.length === 0 ? (
          <p className="muted">No line items were detected for this invoice.</p>
        ) : (
          <table className="lines">
            <thead>
              <tr>
                <th>Part</th>
                <th>Description</th>
                <th>Qty</th>
                <th>Unit cost</th>
                <th>Extended</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {lines.map((line) => (
                <tr key={line.id || line.part_number}>
                  <td>{line.part_number || '—'}</td>
                  <td className="muted">{line.description || '—'}</td>
                  <td>{line.quantity ?? '—'}</td>
                  <td>{formatCurrency(line.unit_cost, currency)}</td>
                  <td>{formatCurrency(line.extended_cost, currency)}</td>
                  <td>
                    <span className={`badge ${line.received ? 'success' : 'warning'}`}>
                      {line.received ? 'Received' : 'Pending'}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      <div className="card">
        <div className="section-header">
          <h4>GL allocations</h4>
          <p className="muted">{allocations.length > 0 ? 'Posting preview' : 'No allocations detected'}</p>
        </div>
        {allocations.length === 0 ? (
          <p className="muted">No allocations detected for this invoice.</p>
        ) : (
          <table className="lines compact">
            <thead>
              <tr>
                <th>Account</th>
                <th>Amount</th>
                <th>Memo</th>
              </tr>
            </thead>
            <tbody>
              {allocations.map((alloc) => (
                <tr key={alloc.account_code}>
                  <td>{alloc.account_code || '—'}</td>
                  <td>{formatCurrency(alloc.amount, currency)}</td>
                  <td className="muted">{alloc.memo || '—'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}
