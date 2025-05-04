-- migrations/20250505_add_import_logs.sql
BEGIN;

CREATE TABLE IF NOT EXISTS import_logs (
  id SERIAL PRIMARY KEY,
  filename TEXT NOT NULL,
  import_type TEXT NOT NULL,          -- e.g. 'quotation_excel' or 'quotation_pdf'
  success_count INTEGER NOT NULL DEFAULT 0,
  failure_count INTEGER NOT NULL DEFAULT 0,
  imported_by INTEGER NOT NULL REFERENCES "user"(id),
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMIT;
