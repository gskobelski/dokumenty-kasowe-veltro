from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, Field, field_validator


class SourceType(str, Enum):
    SALDEO = "saldeo"
    BANK = "bank"


class CashDocumentType(str, Enum):
    KP = "KP"
    KW = "KW"


class DocumentStatus(str, Enum):
    STORED = "stored"
    EXECUTED = "executed"


class RecipientType(str, Enum):
    CONTRACTOR = "contractor"
    EMPLOYEE = "employee"
    OFFICE = "office"
    ONE_TIME_CONTRACTOR = "one_time_contractor"


class ValidationStatus(str, Enum):
    VALID = "valid"
    INVALID = "invalid"
    REQUIRES_REVIEW = "requires_review"


class AppSettings(BaseModel):
    company_name: str = ""
    company_name_short: str = ""
    company_city: str = ""
    company_postal_code: str = ""
    company_address_line: str = ""
    company_tax_id: str = ""
    cash_register_code: str = "KASA"
    cash_register_name: str = "Kasa glowna"
    cash_register_analytics: str = ""
    bank_party_name_short: str = "BANK"
    bank_party_name_full: str = "Podmiot bankowy"
    bank_party_city: str = ""
    bank_party_postal_code: str = ""
    bank_party_address_line: str = ""
    bank_party_tax_id: str = ""


class CashDocumentBase(BaseModel):
    source_type: SourceType
    source_reference: str = ""
    document_type: CashDocumentType
    document_status: DocumentStatus = DocumentStatus.STORED
    issue_date: date
    amount: Decimal = Field(..., gt=0)
    title: str = Field(..., min_length=1, max_length=255)
    description: str = Field(default="", max_length=255)
    recipient_type: RecipientType = RecipientType.CONTRACTOR
    recipient_code: str = ""
    recipient_name_short: str = ""
    recipient_name_full: str = ""
    recipient_city: str = ""
    recipient_postal_code: str = ""
    recipient_address_line: str = ""
    recipient_tax_id: str = ""
    recipient_pesel: str = ""
    category_name: str = ""
    category_subtitle: str = ""
    issuer_name: str = ""
    receiver_name: str = ""
    is_generated: bool = False
    related_issue_date: date | None = None
    comment: str = ""
    notes: str = ""
    ready_for_export: bool = False

    @field_validator("amount", mode="before")
    @classmethod
    def normalize_amount(cls, value: object) -> object:
        if isinstance(value, str):
            return value.replace(",", ".")
        return value


class CashDocumentCreate(CashDocumentBase):
    import_session_id: int | None = None


class CashDocumentUpdate(BaseModel):
    document_status: DocumentStatus | None = None
    title: str | None = Field(default=None, max_length=255)
    description: str | None = Field(default=None, max_length=255)
    recipient_type: RecipientType | None = None
    recipient_code: str | None = None
    recipient_name_short: str | None = None
    recipient_name_full: str | None = None
    recipient_city: str | None = None
    recipient_postal_code: str | None = None
    recipient_address_line: str | None = None
    recipient_tax_id: str | None = None
    recipient_pesel: str | None = None
    category_name: str | None = None
    category_subtitle: str | None = None
    comment: str | None = Field(default=None, max_length=255)
    notes: str | None = Field(default=None, max_length=255)
    ready_for_export: bool | None = None


class CashDocumentRead(CashDocumentBase):
    id: int
    import_session_id: int | None = None
    validation_status: ValidationStatus
    validation_errors: list[str] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime


class ImportSessionSummary(BaseModel):
    id: int
    source_type: SourceType
    filename: str
    imported_at: datetime
    row_count: int
    created_documents_count: int
    ignored_rows_count: int
    unsupported_rows_count: int
    review_required_count: int


class ImportResponse(BaseModel):
    session: ImportSessionSummary
    documents_created: int
    review_required: int
    unsupported: int


class ValidationErrorSummary(BaseModel):
    code: str
    count: int


class ExportResponse(BaseModel):
    file_name: str
    content: str
    exported_count: int

