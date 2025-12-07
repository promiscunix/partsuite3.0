from __future__ import annotations

import logging
from typing import Iterable, List

from sqlalchemy.orm import Session

from app import parser
from app.models import Charges, Files, GLAllocations, InvoiceLines, InvoicePages, Invoices, Parts, Shipments
from app.storage import save_pdf

logger = logging.getLogger(__name__)


def process_upload(db: Session, filename: str, data: bytes) -> Invoices:
    logger.info("Processing upload for %s", filename)
    original_path, summary_path = save_pdf(filename, data)
    invoice_models = []
    for inv in parser.parse_pdf_bytes(data):
        invoice_model = persist_invoice(db, inv, filename, original_path.as_posix(), summary_path.as_posix())
        invoice_models.append(invoice_model)
    db.commit()
    return invoice_models[0]


def persist_invoice(db: Session, invoice_data: parser.Invoice, filename: str, original_path: str, summary_path: str) -> Invoices:
    invoice = Invoices(
        invoice_number=invoice_data.invoice_number,
        invoice_date=invoice_data.invoice_date,
        order_number=invoice_data.order_number,
        vendor_name=invoice_data.vendor_name,
        customer_name=invoice_data.customer_name,
        subtotal=invoice_data.subtotal,
        tax=invoice_data.tax,
        freight=invoice_data.freight,
        total=invoice_data.total,
        parsing_confidence=invoice_data.parsing_confidence,
        raw_text=invoice_data.raw_text,
    )
    db.add(invoice)
    db.flush()

    for page in invoice_data.pages:
        db.add(
            InvoicePages(
                invoice_id=invoice.id,
                page_number=page.page_number,
                text_content=page.text_content,
                is_summary=page.is_summary,
            )
        )

    for line in invoice_data.lines:
        part = get_or_create_part(db, line.part_number, line.description)
        db.add(
            InvoiceLines(
                invoice_id=invoice.id,
                part_id=part.id if part else None,
                part_number=line.part_number,
                description=line.description,
                quantity=line.quantity,
                unit_cost=line.unit_cost,
                extended_cost=line.extended_cost,
            )
        )

    for charge in invoice_data.charges:
        db.add(Charges(invoice_id=invoice.id, type=charge.type, amount=charge.amount))

    for alloc in invoice_data.allocations:
        db.add(
            GLAllocations(
                invoice_id=invoice.id,
                account_code=alloc.account_code,
                amount=alloc.amount,
                memo=alloc.memo,
            )
        )

    db.add(Files(filename=filename, original_path=original_path, summary_path=summary_path, invoice_id=invoice.id))

    db.add(Shipments(invoice_id=invoice.id, description="Auto-created shipment placeholder", received=False))

    logger.info("Persisted invoice %s", invoice.invoice_number)
    return invoice


def get_or_create_part(db: Session, part_number: str, description: str | None):
    part = db.query(Parts).filter_by(part_number=part_number).one_or_none()
    if part is None:
        part = Parts(part_number=part_number, description=description)
        db.add(part)
        db.flush()
    return part


def retryable_process(db: Session, filename: str, data: bytes, attempts: int = 3) -> Invoices:
    last_exc: Exception | None = None
    for _ in range(attempts):
        try:
            return process_upload(db, filename, data)
        except Exception as exc:  # pragma: no cover - logging path
            logger.exception("Error processing upload: %s", exc)
            last_exc = exc
    raise RuntimeError("Failed to process upload") from last_exc


def list_invoices(db: Session) -> List[Invoices]:
    return db.query(Invoices).order_by(Invoices.created_at.desc()).all()


def get_not_received(db: Session):
    return db.query(InvoiceLines, Parts).join(Parts, InvoiceLines.part_id == Parts.id).filter(Parts.received.is_(False)).all()
