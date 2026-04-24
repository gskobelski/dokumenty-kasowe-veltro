import { AppShell } from "../components/app-shell";
import { ExportPanel } from "../components/export-panel";

export default function HomePage() {
  return (
    <AppShell
      title="Przeglad przeplywu import -> korekta -> eksport"
      subtitle="Priorytet MVP to poprawny eksport .epp i szybkie wychwycenie rekordow wymagajacych recznej korekty."
    >
      <div className="grid two">
        <section className="panel stack">
          <h3>Co obsluguje MVP</h3>
          <ul>
            <li>Import Saldeo CSV/XLSX dla faktur gotowkowych.</li>
            <li>Import banku CSV/XLSX dla wplat i wyplat bankomatowych.</li>
            <li>Przeglad i filtracja dokumentow KP/KW.</li>
            <li>Eksport EPP do Rewizora GT.</li>
          </ul>
        </section>
        <ExportPanel />
      </div>
    </AppShell>
  );
}

