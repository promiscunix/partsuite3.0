from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class GLAllocation(ORMModel):
    id: int | None = None
    account_code: str
    amount: float
    memo: Optional[str] = None
    account_description: Optional[str] = None
    cost_center: Optional[str] = None
    department: Optional[str] = None
    internal_account_code: Optional[str] = None

class Charge(ORMModel):
    id: int | None = None
    type: str
    amount: float

class InvoiceLine(ORMModel):
    id: int | None = None
    part_number: str
    description: Optional[str] = None
    quantity: Optional[int] = None
    unit_cost: Optional[float] = None
    list_price: Optional[float] = None
    net_price: Optional[float] = None
    discount_percent: Optional[float] = None
    extended_cost: Optional[float] = None
    uom: Optional[str] = None
    order_reference_id: Optional[int] = None
    part_id: Optional[int] = None

class InvoicePage(ORMModel):
    page_number: int
    text_content: str
    is_summary: bool = False

class Invoice(ORMModel):
    id: int | None = None
    invoice_number: Optional[str] = None
    invoice_date: Optional[date] = None
    order_number: Optional[str] = None
    vendor_name: Optional[str] = None
    customer_name: Optional[str] = None
    billing_period_start: Optional[date] = None
    billing_period_end: Optional[date] = None
    due_date: Optional[date] = None
    currency: Optional[str] = None
    payment_terms: Optional[str] = None
    subtotal: Optional[float] = None
    tax: Optional[float] = None
    freight: Optional[float] = None
    total: Optional[float] = None
    parsing_confidence: float = 0.0
    raw_text: Optional[str] = None
    pages: List[InvoicePage] = Field(default_factory=list)
    lines: List[InvoiceLine] = Field(default_factory=list)
    charges: List[Charge] = Field(default_factory=list)
    allocations: List[GLAllocation] = Field(default_factory=list)
    orders: List["OrderReference"] = Field(default_factory=list)


class OrderReference(ORMModel):
    id: int | None = None
    order_number: str
    order_type: Optional[str] = None
    release_number: Optional[str] = None
    customer_reference: Optional[str] = None


class AccountMapping(ORMModel):
    id: int | None = None
    vendor_name: Optional[str] = None
    vendor_account_code: str
    internal_account_code: str
    effective_date: Optional[date] = None
    notes: Optional[str] = None

class FileRecord(ORMModel):
    id: int
    filename: str
    original_path: str
    summary_path: Optional[str]
    uploaded_at: datetime
    invoice: Optional[Invoice]

class UploadResponse(ORMModel):
    invoice: Invoice
    file: FileRecord


class ParseTrigger(BaseModel):
    file_ids: List[int]
