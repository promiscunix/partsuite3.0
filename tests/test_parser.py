from pathlib import Path

import pytest

pytest.importorskip("pdfminer")

from app import parser  # noqa: E402


def test_is_fca_invoice_detects_keywords():
    text = "This FCA US LLC invoice"
    assert parser.is_fca_invoice(text)


def test_parse_invoice_text_extracts_fields():
    sample = Path("fixtures/sample_invoice.txt").read_bytes()
    invoices = parser.parse_pdf_bytes(sample)
    invoice = invoices[0]
    assert invoice.invoice_number == "12345"
    assert invoice.order_number == "PO-7788"
    assert any(line.part_number == "ABC123" for line in invoice.lines)
    assert any(alloc.account_code == "5000" for alloc in invoice.allocations)
