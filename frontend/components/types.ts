export type CashDocument = {
  id: number;
  source_type: string;
  source_reference: string;
  document_type: string;
  document_status: string;
  issue_date: string;
  amount: string;
  title: string;
  description: string;
  recipient_type: string;
  recipient_code: string;
  recipient_name_short: string;
  recipient_name_full: string;
  recipient_city: string;
  recipient_postal_code: string;
  recipient_address_line: string;
  recipient_tax_id: string;
  recipient_pesel: string;
  category_name: string;
  category_subtitle: string;
  issuer_name: string;
  receiver_name: string;
  is_generated: boolean;
  related_issue_date: string | null;
  comment: string;
  notes: string;
  ready_for_export: boolean;
  import_session_id: number | null;
  validation_status: string;
  validation_errors: string[];
  created_at: string;
  updated_at: string;
};

export type ValidationErrorSummary = {
  code: string;
  count: number;
};

export type AppSettings = {
  company_name: string;
  company_name_short: string;
  company_city: string;
  company_postal_code: string;
  company_address_line: string;
  company_tax_id: string;
  cash_register_code: string;
  cash_register_name: string;
  cash_register_analytics: string;
  bank_party_name_short: string;
  bank_party_name_full: string;
  bank_party_city: string;
  bank_party_postal_code: string;
  bank_party_address_line: string;
  bank_party_tax_id: string;
};

export type ImportSessionSummary = {
  id: number;
  source_type: string;
  filename: string;
  imported_at: string;
  row_count: number;
  created_documents_count: number;
  ignored_rows_count: number;
  unsupported_rows_count: number;
  review_required_count: number;
};

export type ImportResponse = {
  session: ImportSessionSummary;
  documents_created: number;
  review_required: number;
  unsupported: number;
};
