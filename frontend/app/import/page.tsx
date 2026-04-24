import { AppShell } from "../../components/app-shell";
import { ImportPanel } from "../../components/import-panel";

export default function ImportPage() {
  return (
    <AppShell
      title="Import plikow"
      subtitle="Dwa niezalezne wejscia: Saldeo dla faktur gotowkowych oraz bank dla operacji bankomatowych."
    >
      <ImportPanel />
    </AppShell>
  );
}

