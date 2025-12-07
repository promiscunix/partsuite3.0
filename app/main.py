from __future__ import annotations

import logging
from typing import List

from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
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
