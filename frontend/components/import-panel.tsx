"use client";

import { useState } from "react";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

async function uploadFile(endpoint: string, file: File) {
  const formData = new FormData();
  formData.append("file", file);
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    method: "POST",
    body: formData,
  });
  if (!response.ok) {
    throw new Error(await response.text());
  }
  return response.json();
}

export function ImportPanel() {
  const [saldeoFile, setSaldeoFile] = useState<File | null>(null);
  const [bankFile, setBankFile] = useState<File | null>(null);
  const [status, setStatus] = useState<string>("");

  async function handleImport(endpoint: string, file: File | null) {
    if (!file) {
      setStatus("Wybierz plik przed importem.");
      return;
    }
    setStatus("Przetwarzanie...");
    try {
      const result = await uploadFile(endpoint, file);
      setStatus(
        `Utworzono ${result.documents_created} dokumentow, review ${result.review_required}, unsupported ${result.unsupported}.`,
      );
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "Import nie powiodl sie.");
    }
  }

  return (
    <div className="grid two">
      <section className="panel stack">
        <h3>Import Saldeo</h3>
        <p className="muted">CSV lub XLSX z fakturami oplaconymi gotowka.</p>
        <input type="file" accept=".csv,.xlsx" onChange={(event) => setSaldeoFile(event.target.files?.[0] ?? null)} />
        <button className="button" type="button" onClick={() => handleImport("/api/imports/saldeo", saldeoFile)}>
          Importuj Saldeo
        </button>
      </section>
      <section className="panel stack">
        <h3>Import wyciagu bankowego</h3>
        <p className="muted">CSV lub XLSX. System rozpozna wplaty i wyplaty bankomatowe.</p>
        <input type="file" accept=".csv,.xlsx" onChange={(event) => setBankFile(event.target.files?.[0] ?? null)} />
        <button className="button secondary" type="button" onClick={() => handleImport("/api/imports/bank", bankFile)}>
          Importuj bank
        </button>
      </section>
      <section className="panel">
        <h3>Status</h3>
        <p className="muted">{status || "Brak operacji."}</p>
      </section>
    </div>
  );
}

