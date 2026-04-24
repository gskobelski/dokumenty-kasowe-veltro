"use client";

import { useState } from "react";
import { importBank, importSaldeo } from "../lib/api";
import type { ImportResponse } from "./types";

type ImportSource = "saldeo" | "bank";

type ImportStatus =
  | { kind: "idle" }
  | {
      kind: "processing";
      source: ImportSource;
      fileName: string;
      title: string;
      message: string;
    }
  | {
      kind: "success" | "warning";
      source: ImportSource;
      fileName: string;
      title: string;
      message: string;
      result: ImportResponse;
    }
  | {
      kind: "error";
      source?: ImportSource;
      fileName?: string;
      title: string;
      message: string;
    };

export function ImportPanel() {
  const [saldeoFile, setSaldeoFile] = useState<File | null>(null);
  const [bankFile, setBankFile] = useState<File | null>(null);
  const [status, setStatus] = useState<ImportStatus>({ kind: "idle" });
  const isProcessing = status.kind === "processing";

  async function handleImport(source: ImportSource, file: File | null) {
    if (!file) {
      setStatus({
        kind: "error",
        source,
        title: "Brak pliku do importu",
        message: "Wybierz plik CSV albo XLSX przed uruchomieniem importu.",
      });
      return;
    }

    setStatus({
      kind: "processing",
      source,
      fileName: file.name,
      title: `Przetwarzanie pliku ${labelForSource(source)}`,
      message: "Trwa odczyt pliku, klasyfikacja rekordow i zapis dokumentow kasowych.",
    });

    try {
      const result = source === "saldeo" ? await importSaldeo(file) : await importBank(file);
      setStatus(buildCompletedStatus(source, file.name, result));
    } catch (error) {
      setStatus({
        kind: "error",
        source,
        fileName: file.name,
        title: `Import ${labelForSource(source)} nie powiodl sie`,
        message: getErrorMessage(error),
      });
    }
  }

  return (
    <div className="grid two">
      <section className="panel stack">
        <h3>Import Saldeo</h3>
        <p className="muted">CSV lub XLSX z fakturami oplaconymi gotowka.</p>
        <input type="file" accept=".csv,.xlsx" onChange={(event) => setSaldeoFile(event.target.files?.[0] ?? null)} />
        <button className="button" type="button" disabled={isProcessing} onClick={() => handleImport("saldeo", saldeoFile)}>
          {isProcessing && status.source === "saldeo" ? "Przetwarzanie..." : "Importuj Saldeo"}
        </button>
      </section>
      <section className="panel stack">
        <h3>Import wyciagu bankowego</h3>
        <p className="muted">CSV lub XLSX. System rozpozna wplaty i wyplaty bankomatowe.</p>
        <input type="file" accept=".csv,.xlsx" onChange={(event) => setBankFile(event.target.files?.[0] ?? null)} />
        <button className="button secondary" type="button" disabled={isProcessing} onClick={() => handleImport("bank", bankFile)}>
          {isProcessing && status.source === "bank" ? "Przetwarzanie..." : "Importuj bank"}
        </button>
      </section>
      <section className="panel import-status">
        <div className="status-header">
          <span className={`status-icon ${status.kind}`}>
            {status.kind === "success"
              ? "✓"
              : status.kind === "warning"
                ? "!"
                : status.kind === "error"
                  ? "×"
                  : status.kind === "idle"
                    ? "i"
                    : ""}
          </span>
          <div className="stack">
            <h3>Status importu</h3>
            <strong>{statusTitle(status)}</strong>
            <p className="muted">{statusMessage(status)}</p>
          </div>
        </div>

        {"fileName" in status && status.fileName ? (
          <p className="muted">
            Plik: <strong>{status.fileName}</strong>
          </p>
        ) : null}

        {"result" in status ? (
          <div className="status-summary">
            <div className="status-metrics">
              <div className="metric">
                <span className="metric-label">Wiersze</span>
                <strong className="metric-value">{status.result.session.row_count}</strong>
              </div>
              <div className="metric">
                <span className="metric-label">Dokumenty</span>
                <strong className="metric-value">{status.result.documents_created}</strong>
              </div>
              <div className="metric">
                <span className="metric-label">Review</span>
                <strong className="metric-value">{status.result.review_required}</strong>
              </div>
              <div className="metric">
                <span className="metric-label">Unsupported</span>
                <strong className="metric-value">{status.result.unsupported}</strong>
              </div>
            </div>
            {status.kind === "warning" ? (
              <p className="muted">
                Import zakonczyl sie, ale wymaga uwagi. Czesc rekordow nie zostala zamieniona na dokumenty kasowe albo wymaga recznej korekty.
              </p>
            ) : null}
          </div>
        ) : null}
      </section>
    </div>
  );
}

function buildCompletedStatus(
  source: ImportSource,
  fileName: string,
  result: ImportResponse,
): Extract<ImportStatus, { kind: "success" | "warning" }> {
  const hasWarnings = result.review_required > 0 || result.unsupported > 0 || result.documents_created === 0;

  if (hasWarnings) {
    return {
      kind: "warning",
      source,
      fileName,
      result,
      title: `Import ${labelForSource(source)} zakonczyl sie z ostrzezeniami`,
      message: buildResultMessage(result),
    };
  }

  return {
    kind: "success",
    source,
    fileName,
    result,
    title: `Import ${labelForSource(source)} zakonczyl sie powodzeniem`,
    message: buildResultMessage(result),
  };
}

function buildResultMessage(result: ImportResponse): string {
  if (result.documents_created === 0) {
    return "Plik zostal odczytany, ale nie utworzono zadnych dokumentow kasowych.";
  }

  return `Utworzono ${result.documents_created} dokumentow kasowych z ${result.session.row_count} wierszy pliku.`;
}

function getErrorMessage(error: unknown): string {
  if (!(error instanceof Error)) {
    return "Import nie powiodl sie.";
  }

  try {
    const parsed = JSON.parse(error.message) as { detail?: string };
    if (parsed.detail) {
      return parsed.detail;
    }
  } catch {
    return error.message;
  }

  return error.message;
}

function labelForSource(source: ImportSource): string {
  return source === "bank" ? "banku" : "Saldeo";
}

function statusTitle(status: ImportStatus): string {
  if (status.kind === "idle") {
    return "Brak aktywnego importu";
  }
  return status.title;
}

function statusMessage(status: ImportStatus): string {
  if (status.kind === "idle") {
    return "Po wybraniu pliku zobaczysz tutaj postep importu, wynik przetwarzania i ewentualne bledy.";
  }
  return status.message;
}
