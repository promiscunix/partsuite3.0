# FCA Invoice Data Model

The schema below captures the invoice signals mentioned in the FCA PDF packets so they can be parsed, stored, and mapped into downstream accounting and inventory systems.

## Core documents
- **invoices**: one record per FCA invoice. Stores invoice number, invoice date, optional billing period, due date, currency, payment terms, and overall financials (subtotal/tax/freight/total). Links to uploaded files.
- **invoice_pages**: text for each PDF page and a flag for the summary page to support page-level parsing and traceability.
- **order_references**: supports one-to-many order numbers per invoice (e.g., PO, release, or customer references) that FCA often lists together.
- **invoice_lines**: line items with part number, description, quantity, list/net/unit pricing, discount, extended cost, and unit of measure. Each line can reference a specific order to preserve the PO-to-line mapping.
- **parts**: unique catalog of part numbers to normalize descriptions and statuses (billed, invoiced, received).
- **shipments**: high-level receipt tracking for shipments referenced by the invoice.

## Charges and allocations
- **charges**: non-line-item charges (freight, hazmat, environmental) that accompany the invoice total.
- **gl_allocations**: captures the summary page totals by vendor account code. Includes description, cost center/department, and the mapped internal account code to enable GL posting.
- **account_mappings**: reusable lookup that pairs FCA account codes with the internal GL codes and an optional effective date window.

## Relationships
- An invoice can have many pages, lines, order references, charges, GL allocations, and shipments.
- Invoice lines can optionally link back to an order reference and a normalized part record.
- GL allocations link to their invoice while also carrying an internal mapping shortcut so downstream posting does not have to join back to `account_mappings` every time.

## Key fields to extract from each FCA PDF
- Header: invoice number, invoice date, billing period (if present), due date, currency, payment terms, vendor/customer names.
- Orders: every PO/release/customer order number plus any release numbers on the summary page.
- Lines: part number, description, quantity, list price, net price, unit price, discount %, extended amount, and unit of measure.
- Charges: freight/taxes/fees not baked into line items.
- Summary allocations: each account code and amount on the final summary page, with the descriptive text/cost center/department to support GL mapping.

## Usage notes
- The mapping tables allow multiple FCA account codes to roll up to a single internal ledger account without losing the original codes for audit.
- Optional fields keep parsing resilient: when the PDF omits a value, the record can still be created and enriched later.
- Indexes on invoice number, order number, and account codes support lookups for reconciliation and duplicate detection.
