from __future__ import annotations

from datetime import date, datetime
from typing import List, Optional

from sqlalchemy import Boolean, Date, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Files(Base):
    __tablename__ = "files"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    filename: Mapped[str] = mapped_column(String, nullable=False)
    original_path: Mapped[str] = mapped_column(String, nullable=False)
    summary_path: Mapped[Optional[str]] = mapped_column(String)
    uploaded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    invoice_id: Mapped[Optional[int]] = mapped_column(ForeignKey("invoices.id"), nullable=True)

    invoice: Mapped[Optional[Invoices]] = relationship("Invoices", back_populates="file")


class Invoices(Base):
    __tablename__ = "invoices"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    invoice_number: Mapped[Optional[str]] = mapped_column(String, index=True)
    invoice_date: Mapped[Optional[date]] = mapped_column(Date)
    order_number: Mapped[Optional[str]] = mapped_column(String)
    vendor_name: Mapped[Optional[str]] = mapped_column(String)
    customer_name: Mapped[Optional[str]] = mapped_column(String)
    billing_period_start: Mapped[Optional[date]] = mapped_column(Date)
    billing_period_end: Mapped[Optional[date]] = mapped_column(Date)
    due_date: Mapped[Optional[date]] = mapped_column(Date)
    currency: Mapped[Optional[str]] = mapped_column(String(3))
    payment_terms: Mapped[Optional[str]] = mapped_column(String)
    subtotal: Mapped[Optional[float]] = mapped_column(Float)
    tax: Mapped[Optional[float]] = mapped_column(Float)
    freight: Mapped[Optional[float]] = mapped_column(Float)
    total: Mapped[Optional[float]] = mapped_column(Float)
    parsing_confidence: Mapped[float] = mapped_column(Float, default=0.0)
    raw_text: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    pages: Mapped[List[InvoicePages]] = relationship("InvoicePages", back_populates="invoice", cascade="all, delete-orphan")
    lines: Mapped[List[InvoiceLines]] = relationship("InvoiceLines", back_populates="invoice", cascade="all, delete-orphan")
    charges: Mapped[List[Charges]] = relationship("Charges", back_populates="invoice", cascade="all, delete-orphan")
    allocations: Mapped[List[GLAllocations]] = relationship("GLAllocations", back_populates="invoice", cascade="all, delete-orphan")
    shipments: Mapped[List[Shipments]] = relationship("Shipments", back_populates="invoice", cascade="all, delete-orphan")
    orders: Mapped[List[OrderReferences]] = relationship("OrderReferences", back_populates="invoice", cascade="all, delete-orphan")
    file: Mapped[Optional[Files]] = relationship("Files", back_populates="invoice", uselist=False)


class InvoicePages(Base):
    __tablename__ = "invoice_pages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    invoice_id: Mapped[int] = mapped_column(ForeignKey("invoices.id"))
    page_number: Mapped[int] = mapped_column(Integer)
    text_content: Mapped[str] = mapped_column(Text)
    is_summary: Mapped[bool] = mapped_column(Boolean, default=False)

    invoice: Mapped[Invoices] = relationship("Invoices", back_populates="pages")


class Parts(Base):
    __tablename__ = "parts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    part_number: Mapped[str] = mapped_column(String, unique=True, index=True)
    description: Mapped[Optional[str]] = mapped_column(String)
    billed: Mapped[bool] = mapped_column(Boolean, default=False)
    invoiced: Mapped[bool] = mapped_column(Boolean, default=False)
    received: Mapped[bool] = mapped_column(Boolean, default=False)

    lines: Mapped[List[InvoiceLines]] = relationship("InvoiceLines", back_populates="part")


class InvoiceLines(Base):
    __tablename__ = "invoice_lines"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    invoice_id: Mapped[int] = mapped_column(ForeignKey("invoices.id"))
    order_reference_id: Mapped[Optional[int]] = mapped_column(ForeignKey("order_references.id"))
    part_id: Mapped[Optional[int]] = mapped_column(ForeignKey("parts.id"))
    part_number: Mapped[str] = mapped_column(String)
    description: Mapped[Optional[str]] = mapped_column(String)
    quantity: Mapped[Optional[int]] = mapped_column(Integer)
    unit_cost: Mapped[Optional[float]] = mapped_column(Float)
    list_price: Mapped[Optional[float]] = mapped_column(Float)
    net_price: Mapped[Optional[float]] = mapped_column(Float)
    discount_percent: Mapped[Optional[float]] = mapped_column(Float)
    extended_cost: Mapped[Optional[float]] = mapped_column(Float)
    uom: Mapped[Optional[str]] = mapped_column(String)

    invoice: Mapped[Invoices] = relationship("Invoices", back_populates="lines")
    part: Mapped[Optional[Parts]] = relationship("Parts", back_populates="lines")
    order_reference: Mapped[Optional[OrderReferences]] = relationship("OrderReferences", back_populates="lines")


class Shipments(Base):
    __tablename__ = "shipments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    invoice_id: Mapped[int] = mapped_column(ForeignKey("invoices.id"))
    description: Mapped[Optional[str]] = mapped_column(String)
    received: Mapped[bool] = mapped_column(Boolean, default=False)

    invoice: Mapped[Invoices] = relationship("Invoices", back_populates="shipments")


class Charges(Base):
    __tablename__ = "charges"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    invoice_id: Mapped[int] = mapped_column(ForeignKey("invoices.id"))
    type: Mapped[str] = mapped_column(String)
    amount: Mapped[float] = mapped_column(Float)

    invoice: Mapped[Invoices] = relationship("Invoices", back_populates="charges")


class GLAllocations(Base):
    __tablename__ = "gl_allocations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    invoice_id: Mapped[int] = mapped_column(ForeignKey("invoices.id"))
    account_code: Mapped[str] = mapped_column(String)
    amount: Mapped[float] = mapped_column(Float)
    memo: Mapped[Optional[str]] = mapped_column(String)
    account_description: Mapped[Optional[str]] = mapped_column(String)
    cost_center: Mapped[Optional[str]] = mapped_column(String)
    department: Mapped[Optional[str]] = mapped_column(String)
    internal_account_code: Mapped[Optional[str]] = mapped_column(String)

    invoice: Mapped[Invoices] = relationship("Invoices", back_populates="allocations")


class AccountMappings(Base):
    __tablename__ = "account_mappings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    vendor_name: Mapped[Optional[str]] = mapped_column(String)
    vendor_account_code: Mapped[str] = mapped_column(String, index=True)
    internal_account_code: Mapped[str] = mapped_column(String, index=True)
    effective_date: Mapped[Optional[date]] = mapped_column(Date)
    notes: Mapped[Optional[str]] = mapped_column(String)


class OrderReferences(Base):
    __tablename__ = "order_references"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    invoice_id: Mapped[int] = mapped_column(ForeignKey("invoices.id"))
    order_number: Mapped[str] = mapped_column(String, index=True)
    order_type: Mapped[Optional[str]] = mapped_column(String)
    release_number: Mapped[Optional[str]] = mapped_column(String)
    customer_reference: Mapped[Optional[str]] = mapped_column(String)

    invoice: Mapped[Invoices] = relationship("Invoices", back_populates="orders")
    lines: Mapped[List[InvoiceLines]] = relationship("InvoiceLines", back_populates="order_reference")
