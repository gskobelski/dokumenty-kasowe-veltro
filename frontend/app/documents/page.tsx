import { AppShell } from "../../components/app-shell";
import { DocumentEditor } from "../../components/document-editor";
import { DocumentTable } from "../../components/document-table";
import type { CashDocument } from "../../components/types";
import { listDocuments, listValidationErrors } from "../../lib/api";

export default async function DocumentsPage() {
  let documents: CashDocument[] = [];
  let errors: Array<{ code: string; count: number }> = [];

  try {
    documents = await listDocuments();
    errors = await listValidationErrors();
  } catch {
    documents = [];
    errors = [];
  }

  return (
    <AppShell
      title="Dokumenty kasowe"
      subtitle="Lista dokumentow po imporcie. Tutaj operator widzi rekordy blokowane przez walidacje i przygotowuje partie do eksportu."
    >
      <div className="grid two">
        <div className="stack">
          <DocumentTable documents={documents} />
          <section className="panel stack">
            <h3>Najczestsze blokady</h3>
            {errors.length === 0 ? (
              <p className="muted">Brak danych albo brak blokad.</p>
            ) : (
              errors.map((item) => (
                <div key={item.code} className="button-row">
                  <span className="tag">{item.code}</span>
                  <span>{item.count}</span>
                </div>
              ))
            )}
          </section>
        </div>
        <DocumentEditor />
      </div>
    </AppShell>
  );
}

