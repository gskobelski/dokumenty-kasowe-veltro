"use client";

import { useState } from "react";

import { saveSettings } from "../lib/api";
import type { AppSettings } from "./types";

export function SettingsForm({ initialSettings }: { initialSettings: AppSettings | null }) {
  const [form, setForm] = useState<AppSettings>(
    initialSettings ?? {
      company_name: "",
      company_name_short: "",
      company_city: "",
      company_postal_code: "",
      company_address_line: "",
      company_tax_id: "",
      cash_register_code: "KASA",
      cash_register_name: "Kasa glowna",
      cash_register_analytics: "",
      bank_party_name_short: "BANK",
      bank_party_name_full: "Podmiot bankowy",
      bank_party_city: "",
      bank_party_postal_code: "",
      bank_party_address_line: "",
      bank_party_tax_id: "",
    },
  );
  const [status, setStatus] = useState<string>("");
  const [isSaving, setIsSaving] = useState(false);

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsSaving(true);
    setStatus("Zapisywanie ustawien...");
    try {
      const saved = await saveSettings(form);
      setForm(saved);
      setStatus("Ustawienia zapisane. Mozesz teraz przygotowac dokumenty bankowe do eksportu.");
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "Nie udalo sie zapisac ustawien.");
    } finally {
      setIsSaving(false);
    }
  }

  function updateField<Key extends keyof AppSettings>(key: Key, value: AppSettings[Key]) {
    setForm((current) => ({ ...current, [key]: value }));
  }

  return (
    <form className="stack" onSubmit={handleSubmit}>
      <section className="panel stack">
        <h3>Dane firmy</h3>
        <div className="grid two">
          <div className="field">
            <label htmlFor="company_name">Pelna nazwa</label>
            <input id="company_name" value={form.company_name} onChange={(event) => updateField("company_name", event.target.value)} />
          </div>
          <div className="field">
            <label htmlFor="company_name_short">Nazwa skrocona</label>
            <input id="company_name_short" value={form.company_name_short} onChange={(event) => updateField("company_name_short", event.target.value)} />
          </div>
          <div className="field">
            <label htmlFor="company_city">Miasto</label>
            <input id="company_city" value={form.company_city} onChange={(event) => updateField("company_city", event.target.value)} />
          </div>
          <div className="field">
            <label htmlFor="company_postal_code">Kod pocztowy</label>
            <input id="company_postal_code" value={form.company_postal_code} onChange={(event) => updateField("company_postal_code", event.target.value)} />
          </div>
          <div className="field">
            <label htmlFor="company_address_line">Adres</label>
            <input id="company_address_line" value={form.company_address_line} onChange={(event) => updateField("company_address_line", event.target.value)} />
          </div>
          <div className="field">
            <label htmlFor="company_tax_id">NIP</label>
            <input id="company_tax_id" value={form.company_tax_id} onChange={(event) => updateField("company_tax_id", event.target.value)} />
          </div>
        </div>
      </section>

      <section className="panel stack">
        <h3>Dane kasy</h3>
        <div className="grid two">
          <div className="field">
            <label htmlFor="cash_register_code">Kod kasy</label>
            <input id="cash_register_code" value={form.cash_register_code} onChange={(event) => updateField("cash_register_code", event.target.value)} />
          </div>
          <div className="field">
            <label htmlFor="cash_register_name">Nazwa kasy</label>
            <input id="cash_register_name" value={form.cash_register_name} onChange={(event) => updateField("cash_register_name", event.target.value)} />
          </div>
          <div className="field">
            <label htmlFor="cash_register_analytics">Analityka</label>
            <input id="cash_register_analytics" value={form.cash_register_analytics} onChange={(event) => updateField("cash_register_analytics", event.target.value)} />
          </div>
        </div>
      </section>

      <section className="panel stack">
        <h3>Podmiot bankowy dla wyplat i wplat</h3>
        <p className="muted">
          Te pola sa potrzebne, zeby dokumenty bankowe przeszly walidacje i mogly trafic do eksportu EPP.
        </p>
        <div className="grid two">
          <div className="field">
            <label htmlFor="bank_party_name_full">Pelna nazwa</label>
            <input id="bank_party_name_full" value={form.bank_party_name_full} onChange={(event) => updateField("bank_party_name_full", event.target.value)} />
          </div>
          <div className="field">
            <label htmlFor="bank_party_name_short">Nazwa skrocona</label>
            <input id="bank_party_name_short" value={form.bank_party_name_short} onChange={(event) => updateField("bank_party_name_short", event.target.value)} />
          </div>
          <div className="field">
            <label htmlFor="bank_party_city">Miasto</label>
            <input id="bank_party_city" value={form.bank_party_city} onChange={(event) => updateField("bank_party_city", event.target.value)} />
          </div>
          <div className="field">
            <label htmlFor="bank_party_postal_code">Kod pocztowy</label>
            <input id="bank_party_postal_code" value={form.bank_party_postal_code} onChange={(event) => updateField("bank_party_postal_code", event.target.value)} />
          </div>
          <div className="field">
            <label htmlFor="bank_party_address_line">Adres</label>
            <input id="bank_party_address_line" value={form.bank_party_address_line} onChange={(event) => updateField("bank_party_address_line", event.target.value)} />
          </div>
          <div className="field">
            <label htmlFor="bank_party_tax_id">NIP</label>
            <input id="bank_party_tax_id" value={form.bank_party_tax_id} onChange={(event) => updateField("bank_party_tax_id", event.target.value)} />
          </div>
        </div>
      </section>

      <section className="panel stack">
        <div className="button-row">
          <button className="button" type="submit" disabled={isSaving}>
            {isSaving ? "Zapisywanie..." : "Zapisz ustawienia"}
          </button>
        </div>
        <p className="muted">{status || "Uzupelnij ustawienia firmy i podmiotu bankowego."}</p>
      </section>
    </form>
  );
}
