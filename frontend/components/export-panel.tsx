"use client";

import { useEffect, useState } from "react";

import { API_BASE_URL, getSettings, listDocuments, listValidationErrors, prepareBankExport } from "../lib/api";
import type { AppSettings, CashDocument, PrepareExportResponse, ValidationErrorSummary } from "./types";

type ExportState =
  | { kind: "idle"; message: string }
  | { kind: "processing"; message: string }
  | { kind: "success"; message: string; result: PrepareExportResponse | null }
  | { kind: "error"; message: string };

export function ExportPanel() {
  const [documents, setDocuments] = useState<CashDocument[]>([]);
  const [errors, setErrors] = useState<ValidationErrorSummary[]>([]);
  const [settings, setSettings] = useState<AppSettings | null>(null);
  const [state, setState] = useState<ExportState>({
    kind: "idle",
    message: "Sprawdz, czy ustawienia bankowe sa kompletne, a dokumenty gotowe do eksportu.",
  });

  const readyDocuments = documents.filter(
    (document) => document.ready_for_export && document.validation_status === "valid",
  );
  const bankDocuments = documents.filter((document) => document.source_type === "bank");
  const missingBankSettings = settings
    ? [
        !settings.bank_party_city.trim() ? "miasto podmiotu bankowego" : null,
        !settings.bank_party_postal_code.trim() ? "kod pocztowy podmiotu bankowego" : null,
        !settings.bank_party_address_line.trim() ? "adres podmiotu bankowego" : null,
      ].filter(Boolean)
    : [];

  useEffect(() => {
    void refreshSummary();
  }, []);

  async function refreshSummary() {
    try {
      const [loadedDocuments, loadedErrors, loadedSettings] = await Promise.all([
        listDocuments(),
        listValidationErrors(),
        getSettings(),
      ]);
      setDocuments(loadedDocuments);
      setErrors(loadedErrors);
      setSettings(loadedSettings);
    } catch (error) {
      setState({
        kind: "error",
        message: error instanceof Error ? error.message : "Nie udalo sie pobrac statusu eksportu.",
      });
    }
  }

  async function handlePrepare() {
    setState({ kind: "processing", message: "Uzupelniam dokumenty bankowe z ustawien i przygotowuje je do eksportu..." });
    try {
      const result = await prepareBankExport();
      await refreshSummary();
      setState({
        kind: "success",
        result,
        message: `Przygotowano ${result.ready_count} dokumentow. Zablokowanych pozostalo ${result.blocked_count}.`,
      });
    } catch (error) {
      setState({
        kind: "error",
        message: error instanceof Error ? error.message : "Nie udalo sie przygotowac dokumentow do eksportu.",
      });
    }
  }

  return (
    <section className="panel stack">
      <h3>Eksport EPP</h3>
      <p className="muted">
        Backend generuje plik kompatybilny z Rewizorem GT pod endpointem <code>/api/export/epp</code>.
      </p>

      <div className="status-metrics">
        <div className="metric">
          <span className="metric-label">Gotowe do eksportu</span>
          <strong className="metric-value">{readyDocuments.length}</strong>
        </div>
        <div className="metric">
          <span className="metric-label">Dokumenty bankowe</span>
          <strong className="metric-value">{bankDocuments.length}</strong>
        </div>
        <div className="metric">
          <span className="metric-label">Blokady</span>
          <strong className="metric-value">{errors.reduce((sum, item) => sum + item.count, 0)}</strong>
        </div>
      </div>

      {missingBankSettings.length > 0 ? (
        <p className="muted">
          Brakuje ustawien bankowych: {missingBankSettings.join(", ")}. Uzupelnij je w zakladce Ustawienia.
        </p>
      ) : null}

      {errors.length > 0 ? (
        <div className="stack">
          <strong>Najczestsze blokery</strong>
          {errors.map((item) => (
            <div key={item.code} className="button-row">
              <span className="tag">{item.code}</span>
              <span>{item.count}</span>
            </div>
          ))}
        </div>
      ) : null}

      <div className="button-row">
        <button className="button secondary" type="button" disabled={state.kind === "processing"} onClick={() => void handlePrepare()}>
          {state.kind === "processing" ? "Przygotowywanie..." : "Przygotuj dokumenty bankowe"}
        </button>
        <a className="button" href={`${API_BASE_URL}/api/export/epp`}>
          Pobierz .epp
        </a>
      </div>

      <p className="muted">{state.message}</p>
      <p className="muted">
        Rewizor GT: Narzedzia -&gt; Import -&gt; Plik komunikacji.
      </p>
    </section>
  );
}
