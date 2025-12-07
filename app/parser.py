from __future__ import annotations

import re
from datetime import datetime
from io import BytesIO
from typing import Iterable, List, Optional

from pdfminer.high_level import extract_text

from app.schemas import Charge, GLAllocation, Invoice, InvoiceLine, InvoicePage


FCA_HINTS = ["FCA", "FCA US LLC", "FCA Invoice", "FCA Canada"]


def is_fca_invoice(text: str) -> bool:
    return any(hint.lower() in text.lower() for hint in FCA_HINTS)


def extract_text_from_pdf(data: bytes) -> str:
    try:
        return extract_text(BytesIO(data)) or ""
    except Exception:
        try:
            return data.decode("utf-8", errors="ignore")
        except Exception:
            return ""


def segment_pages(text: str) -> List[str]:
    segments: List[str] = []
    buffer: List[str] = []
    for line in text.splitlines():
        if re.search(r"Page\s+\d+", line) and buffer:
            segments.append("\n".join(buffer))
            buffer = [line]
        else:
            buffer.append(line)
    if buffer:
        segments.append("\n".join(buffer))
    return segments or [text]


def parse_invoice_text(text: str) -> Invoice:
    pages = [InvoicePage(page_number=i + 1, text_content=segment, is_summary=is_summary_page(segment)) for i, segment in enumerate(segment_pages(text))]
    header = text.split("\n")[:20]
    invoice_number = search_first(header, r"Invoice\s*#:?\s*([\w-]+)")
    invoice_date_raw = search_first(header, r"Date\s*:?\s*([\d/.-]{6,10})")
    invoice_date = None
    if invoice_date_raw:
        for fmt in ("%m/%d/%Y", "%Y-%m-%d", "%m-%d-%Y"):
            try:
                invoice_date = datetime.strptime(invoice_date_raw, fmt).date()
                break
            except ValueError:
                continue

    order_number = search_first(text, r"(?:PO|Order)\s*#:?\s*([\w-]+)")
    vendor = search_first(text, r"Vendor\s*:?\s*([\w\s,&.]+)")
    customer = search_first(text, r"Customer\s*:?\s*([\w\s,&.]+)")

    subtotal = to_float(search_first(text, r"Subtotal\s*:?\s*([\d,.]+)"))
    tax = to_float(search_first(text, r"Tax\s*:?\s*([\d,.]+)"))
    freight = to_float(search_first(text, r"Freight\s*:?\s*([\d,.]+)"))
    total = to_float(search_first(text, r"Total\s*:?\s*([\d,.]+)"))

    lines = extract_line_items(text)
    charges = extract_charges(text)
    allocations = extract_allocations(text)

    confidence = 0.5 + 0.1 * sum(bool(x) for x in [invoice_number, invoice_date, order_number])
    if is_fca_invoice(text):
        confidence += 0.2

    return Invoice(
        invoice_number=invoice_number,
        invoice_date=invoice_date,
        order_number=order_number,
        vendor_name=vendor,
        customer_name=customer,
        subtotal=subtotal,
        tax=tax,
        freight=freight,
        total=total,
        parsing_confidence=min(confidence, 1.0),
        raw_text=text,
        pages=pages,
        lines=lines,
        charges=charges,
        allocations=allocations,
    )


def extract_line_items(text: str) -> List[InvoiceLine]:
    lines: List[InvoiceLine] = []
    pattern = re.compile(r"(?P<part>\w{3,})\s+(?P<qty>\d+)\s+(?P<price>[\d,.]+)\s+(?P<ext>[\d,.]+)")
    for match in pattern.finditer(text):
        part_number = match.group("part")
        qty = int(match.group("qty"))
        unit_cost = to_float(match.group("price"))
        extended = to_float(match.group("ext"))
        lines.append(
            InvoiceLine(
                part_number=part_number,
                quantity=qty,
                unit_cost=unit_cost,
                extended_cost=extended,
                description=f"Auto-extracted line for {part_number}",
            )
        )
    return lines


def extract_charges(text: str) -> List[Charge]:
    charges: List[Charge] = []
    for label in ["Freight", "Tax", "Fees"]:
        amount = search_first(text, rf"{label}\s*:?\s*([\d,.]+)")
        if amount:
            charges.append(Charge(type=label.lower(), amount=to_float(amount) or 0.0))
    return charges


def extract_allocations(text: str) -> List[GLAllocation]:
    allocations: List[GLAllocation] = []
    pattern = re.compile(r"(?m)^GL\s*(?P<acct>\d{3,})\s+(?P<amount>[\d,.]+)\s*(?P<memo>.*)$")
    for line in text.splitlines():
        match = pattern.match(line)
        if match:
            allocations.append(
                GLAllocation(
                    account_code=match.group("acct"),
                    amount=to_float(match.group("amount")) or 0.0,
                    memo=match.group("memo").strip() or None,
                )
            )
    return allocations


def is_summary_page(text: str) -> bool:
    markers = ["Summary", "GL", "Allocation"]
    return any(marker.lower() in text.lower() for marker in markers)


def search_first(source: str | Iterable[str], pattern: str) -> Optional[str]:
    text = source if isinstance(source, str) else "\n".join(source)
    match = re.search(pattern, text, re.IGNORECASE)
    return match.group(1).strip() if match else None


def to_float(value: Optional[str]) -> Optional[float]:
    if value is None:
        return None
    try:
        return float(value.replace(",", ""))
    except ValueError:
        return None


def parse_pdf_bytes(data: bytes) -> List[Invoice]:
    text = extract_text_from_pdf(data)
    invoices: List[Invoice] = []
    for segment in split_invoices(text):
        invoices.append(parse_invoice_text(segment))
    return invoices


def split_invoices(text: str) -> List[str]:
    chunks: List[str] = []
    current: List[str] = []
    for line in text.splitlines():
        if re.search(r"Invoice\s*#", line) and current:
            chunks.append("\n".join(current))
            current = [line]
        else:
            current.append(line)
    if current:
        chunks.append("\n".join(current))
    return chunks or [text]
