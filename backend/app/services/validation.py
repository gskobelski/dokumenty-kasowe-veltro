from __future__ import annotations

from app.schemas import CashDocumentRead, RecipientType, ValidationStatus


def validate_document(document: CashDocumentRead) -> list[str]:
    errors: list[str] = []
    if not document.title.strip():
        errors.append("missing_title")
    if document.amount <= 0:
        errors.append("invalid_amount")
    if not document.issue_date:
        errors.append("missing_issue_date")

    if document.recipient_type in {
        RecipientType.CONTRACTOR,
        RecipientType.ONE_TIME_CONTRACTOR,
    }:
        if not document.recipient_name_short.strip():
            errors.append("missing_recipient_name_short")
        if not document.recipient_name_full.strip():
            errors.append("missing_recipient_name_full")
        if not document.recipient_city.strip():
            errors.append("missing_recipient_city")
        if not document.recipient_postal_code.strip():
            errors.append("missing_recipient_postal_code")
        if not document.recipient_address_line.strip():
            errors.append("missing_recipient_address_line")
    elif document.recipient_type == RecipientType.EMPLOYEE:
        if not document.recipient_pesel.strip():
            errors.append("missing_employee_pesel")
        if not document.recipient_name_full.strip():
            errors.append("missing_employee_name")
    elif document.recipient_type == RecipientType.OFFICE:
        if not document.recipient_name_full.strip():
            errors.append("missing_office_name")
        if not document.recipient_city.strip():
            errors.append("missing_office_city")

    return errors


def derive_validation_status(errors: list[str]) -> ValidationStatus:
    if not errors:
        return ValidationStatus.VALID
    return ValidationStatus.REQUIRES_REVIEW

