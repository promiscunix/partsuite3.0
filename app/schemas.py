from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class GLAllocation(BaseModel):
    id: int | None = None
    account_code: str
    amount: float
    memo: Optional[str] = None

    class Config:
        orm_mode = True


class Charge(BaseModel):
    id: int | None = None
    type: str
    amount: float

    class Config:
        orm_mode = True


class InvoiceLine(BaseModel):
    id: int | None = None
    part_number: str
    description: Optional[str] = None
    quantity: Optional[int] = None
    unit_cost: Optional[float] = None
    extended_cost: Optional[float] = None
    part_id: Optional[int] = None

    class Config:
        orm_mode = True


class InvoicePage(BaseModel):
    page_number: int
    text_content: str
    is_summary: bool = False

    class Config:
        orm_mode = True


class Invoice(BaseModel):
    id: int | None = None
    invoice_number: Optional[str] = None
    invoice_date: Optional[date] = None
    order_number: Optional[str] = None
    vendor_name: Optional[str] = None
    customer_name: Optional[str] = None
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

    class Config:
        orm_mode = True


class FileRecord(BaseModel):
    id: int
    filename: str
    original_path: str
    summary_path: Optional[str]
    uploaded_at: datetime
    invoice: Optional[Invoice]

    class Config:
        orm_mode = True


class UploadResponse(BaseModel):
    invoice: Invoice
    file: FileRecord


class ParseTrigger(BaseModel):
    file_ids: List[int]
