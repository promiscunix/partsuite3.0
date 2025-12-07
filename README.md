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

Install dependencies and run:

```bash
cd frontend
pnpm install
pnpm dev
```

After building the frontend (`pnpm build`), the bundled UI is served by Uvicorn at http://localhost:8000/ui (with assets under /assets).

## Testing

Run unit and API integration tests:

```bash
pytest
```

## Fixtures

Sample FCA-style invoice text lives in `fixtures/sample_invoice.txt` and seeds parser tests and development uploads.
