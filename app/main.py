from __future__ import annotations

import logging
from typing import List

from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse, HTMLResponse
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import Base, engine, get_db
from app.models import Files, Invoices, Parts
from app.schemas import FileRecord, Invoice as InvoiceSchema, ParseTrigger, UploadResponse
from app.services import list_invoices, retryable_process

logging.basicConfig(level=logging.INFO)
settings = get_settings()

Base.metadata.create_all(bind=engine)
app = FastAPI(title="Invoice Parser API")


def serialize_invoice(invoice: Invoices) -> InvoiceSchema:
    return InvoiceSchema.from_orm(invoice)


def serialize_file(file: Files) -> FileRecord:
    file.invoice = file.invoice  # ensure lazy load
    return FileRecord.from_orm(file)


@app.post("/upload", response_model=List[UploadResponse])
def upload_files(files: List[UploadFile] = File(...), db: Session = Depends(get_db)):
    results: List[UploadResponse] = []
    for upload in files:
        data = upload.file.read()
        invoice = retryable_process(db, upload.filename, data)
        record = db.query(Files).filter_by(invoice_id=invoice.id).order_by(Files.uploaded_at.desc()).first()
        results.append(UploadResponse(invoice=serialize_invoice(invoice), file=serialize_file(record)))
    return results


@app.get("/")
def root() -> dict[str, str]:
    """Basic landing endpoint to indicate the API is running."""

    return {
        "message": "Invoice Parser API is running. Use POST /upload to submit files.",
        "docs": "/docs",
        "ui": "/upload-ui",
    }


@app.get("/upload")
def upload_instructions() -> dict[str, str]:
    """Explain how to use the upload endpoint when accessed via GET."""

    return {
        "detail": "Upload PDFs with a multipart/form-data POST request to /upload.",
        "example": "curl -F 'files=@invoice.pdf' http://localhost:8000/upload",
    }


@app.get("/upload-ui", response_class=HTMLResponse)
def upload_ui() -> str:
    """Simple browser UI for uploading PDFs to the parser API."""

    return """
<!DOCTYPE html>
<html lang=\"en\">
  <head>
    <meta charset=\"UTF-8\" />
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\" />
    <title>Invoice Parser Upload</title>
    <style>
      :root {
        color: #140f1a;
        background: #f7f4f1;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
      }
      body {
        margin: 0;
        display: flex;
        justify-content: center;
        padding: 32px 16px;
      }
      .panel {
        max-width: 720px;
        width: 100%;
        background: #fff;
        border-radius: 16px;
        padding: 32px;
        box-shadow: 0 20px 50px rgba(20, 15, 26, 0.08);
        border: 1px solid #ece7e3;
      }
      h1 {
        margin: 0 0 8px;
        font-size: 28px;
        letter-spacing: -0.02em;
      }
      p {
        margin: 0 0 16px;
        color: #4c3f55;
      }
      .dropzone {
        margin-top: 12px;
        border: 2px dashed #c096ff;
        background: linear-gradient(135deg, rgba(255, 214, 153, 0.25), rgba(192, 150, 255, 0.18));
        border-radius: 14px;
        padding: 32px;
        text-align: center;
        cursor: pointer;
        transition: border-color 120ms ease, transform 120ms ease;
      }
      .dropzone:hover,
      .dropzone:focus-within {
        border-color: #9b6bff;
        transform: translateY(-2px);
      }
      .actions {
        display: flex;
        gap: 12px;
        margin-top: 16px;
        flex-wrap: wrap;
      }
      button {
        appearance: none;
        border: none;
        padding: 12px 16px;
        border-radius: 10px;
        font-weight: 600;
        cursor: pointer;
        box-shadow: 0 10px 30px rgba(64, 38, 104, 0.12);
      }
      button.primary {
        background: linear-gradient(120deg, #ffb347, #c096ff);
        color: #1d1028;
      }
      button.secondary {
        background: #f2e8ff;
        color: #412f65;
        border: 1px solid #e0d2ff;
      }
      ul {
        list-style: none;
        padding: 0;
        margin: 16px 0 0;
        color: #5a4a6c;
        font-size: 14px;
      }
      .status {
        margin-top: 10px;
        padding: 10px 12px;
        border-radius: 10px;
        background: #f7f2ff;
        border: 1px solid #e3d8ff;
        color: #3e2d62;
        min-height: 20px;
      }
      .small {
        font-size: 14px;
      }
      .muted {
        color: #6c5b7c;
      }
    </style>
  </head>
  <body>
    <div class=\"panel\">
      <h1>Invoice Parser</h1>
      <p class=\"muted\">Upload one or more PDF invoices and we will parse them instantly.</p>
      <div
        id=\"dropzone\"
        class=\"dropzone\"
        tabindex=\"0\"
        role=\"button\"
        aria-label=\"Choose or drop PDF files to upload\"
      >
        <strong>Drop PDFs</strong> or click to browse
        <input id=\"file-input\" type=\"file\" accept=\"application/pdf\" multiple style=\"display: none\" />
      </div>
      <div class=\"actions\">
        <button class=\"secondary\" id=\"clear-btn\">Clear selection</button>
        <button class=\"primary\" id=\"upload-btn\">Upload to /upload</button>
      </div>
      <ul id=\"file-list\"></ul>
      <div class=\"status small\" id=\"status\"></div>
      <p class=\"small muted\">Need API docs? Visit <a href=\"/docs\">/docs</a>.</p>
    </div>

    <script>
      const dropzone = document.getElementById('dropzone');
      const fileInput = document.getElementById('file-input');
      const fileList = document.getElementById('file-list');
      const statusBox = document.getElementById('status');
      const clearBtn = document.getElementById('clear-btn');
      const uploadBtn = document.getElementById('upload-btn');
      let selectedFiles = [];

      const renderList = () => {
        fileList.innerHTML = '';
        selectedFiles.forEach((file) => {
          const item = document.createElement('li');
          item.textContent = file.name;
          fileList.appendChild(item);
        });
      };

      const setStatus = (msg) => {
        statusBox.textContent = msg;
      };

      const handleFiles = (files) => {
        const pdfs = Array.from(files).filter((file) => file.type === 'application/pdf' || file.name.toLowerCase().endsWith('.pdf'));
        if (!pdfs.length) {
          setStatus('Please choose PDF files only.');
          return;
        }
        selectedFiles = [...selectedFiles, ...pdfs];
        renderList();
        setStatus(`${selectedFiles.length} PDF${selectedFiles.length === 1 ? '' : 's'} ready to upload.`);
      };

      dropzone.addEventListener('click', () => fileInput.click());
      dropzone.addEventListener('keydown', (event) => {
        if (event.key === 'Enter' || event.key === ' ') {
          event.preventDefault();
          fileInput.click();
        }
      });
      dropzone.addEventListener('dragover', (event) => {
        event.preventDefault();
      });
      dropzone.addEventListener('drop', (event) => {
        event.preventDefault();
        handleFiles(event.dataTransfer.files);
      });
      fileInput.addEventListener('change', (event) => handleFiles(event.target.files));

      clearBtn.addEventListener('click', () => {
        selectedFiles = [];
        renderList();
        fileInput.value = '';
        setStatus('Selection cleared.');
      });

      uploadBtn.addEventListener('click', async () => {
        if (!selectedFiles.length) {
          setStatus('Pick at least one PDF first.');
          return;
        }
        const form = new FormData();
        selectedFiles.forEach((file) => form.append('files', file));
        setStatus('Uploading…');
        uploadBtn.disabled = true;
        clearBtn.disabled = true;
        try {
          const response = await fetch('/upload', { method: 'POST', body: form });
          if (!response.ok) {
            throw new Error('Upload failed');
          }
          await response.json();
          setStatus('Uploaded and parsed! You can check results at /invoices.');
          selectedFiles = [];
          renderList();
          fileInput.value = '';
        } catch (err) {
          setStatus(err.message || 'Upload failed');
        } finally {
          uploadBtn.disabled = false;
          clearBtn.disabled = false;
        }
      });
    </script>
  </body>
</html>
    """


@app.post("/parse/trigger", response_model=List[InvoiceSchema])
def trigger_parse(body: ParseTrigger, db: Session = Depends(get_db)):
    invoices: List[InvoiceSchema] = []
    for file_id in body.file_ids:
        file = db.query(Files).get(file_id)
        if not file:
            raise HTTPException(status_code=404, detail=f"File {file_id} not found")
        with open(file.original_path, "rb") as f:
            data = f.read()
        invoice = retryable_process(db, file.filename, data)
        invoices.append(serialize_invoice(invoice))
    return invoices


@app.get("/invoices", response_model=List[InvoiceSchema])
def list_parsed_invoices(db: Session = Depends(get_db)):
    return [serialize_invoice(inv) for inv in list_invoices(db)]


@app.get("/invoices/{invoice_id}", response_model=InvoiceSchema)
def get_invoice(invoice_id: int, db: Session = Depends(get_db)):
    invoice = db.query(Invoices).get(invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return serialize_invoice(invoice)


@app.get("/files/{file_id}")
def get_file(file_id: int, db: Session = Depends(get_db)):
    file = db.query(Files).get(file_id)
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(path=file.original_path, filename=file.filename, media_type="application/pdf")


@app.get("/reports/not-received")
def not_received_report(db: Session = Depends(get_db)):
    entries = db.query(Parts).filter(Parts.received.is_(False)).all()
    return [{"part_number": part.part_number, "description": part.description, "received": part.received} for part in entries]
