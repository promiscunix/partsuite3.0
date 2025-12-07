# PartSuite 3.0

A lightweight FastAPI + React prototype for uploading and parsing FCA-style invoices. The backend stores uploads, extracts invoice data, and exposes endpoints for reviewing parsed results while the frontend presents an orange/purple/mocha themed UI.

## Development environment

A Nix shell is provided with Python 3.11, FastAPI, pdfminer.six, pypdf, SQLAlchemy, and pnpm/Node.js for the Vite UI.

```bash
nix-shell
```

With flakes enabled you can enter the same environment via:

```bash
nix develop
```

## Backend

Run the API:

```bash
uvicorn app.main:app --reload
```

### Endpoints
- `POST /upload` – upload one or more PDFs, triggers parse and persistence.
- `POST /parse/trigger` – reprocess stored files by ID.
- `GET /invoices` and `GET /invoices/{id}` – retrieve parsed invoices.
- `GET /files/{id}` – download stored PDFs.
- `GET /reports/not-received` – parts still marked not received.

### Schema
SQLAlchemy models cover invoices, pages, lines, parts (with billed/invoiced/received flags), shipments/receipts, charges, GL allocations, and stored file paths.

## Parser

The parser uses pdfminer.six to read PDFs (with UTF-8 fallback) and applies FCA heuristics, regex-driven field extraction, line-item parsing, GL allocation detection, and summary-page tagging. Multi-invoice files are segmented by header patterns.

## Frontend

The `frontend` folder contains a Vite/React interface with:
- Multi-file upload form.
- Parsed invoice list and detail view with totals and line items.
- "Not received" report filtered by part number.

Install dependencies and run (with the API running on http://localhost:8000):

```bash
cd frontend
pnpm install
pnpm dev
```

Once the dev server starts, open the UI at http://localhost:5173. From the home screen, choose **Review Invoices** to see the invoice table and open the detail view with the highlights, first five part numbers, and last-page summary. The frontend defaults to the backend at `http://localhost:8000`; set `VITE_API_BASE` if your API runs elsewhere.

## Testing

Run unit and API integration tests:

```bash
pytest
```

## Fixtures

Sample FCA-style invoice text lives in `fixtures/sample_invoice.txt` and seeds parser tests and development uploads.
