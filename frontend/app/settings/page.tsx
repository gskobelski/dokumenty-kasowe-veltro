import { AppShell } from "../../components/app-shell";
import { getSettings } from "../../lib/api";

export default async function SettingsPage() {
  const settings = await getSettings().catch(() => null);

  return (
    <AppShell
      title="Ustawienia podstawowe"
      subtitle="Dane firmy, kasy i stalego podmiotu bankowego wykorzystywane w eksporcie EPP."
    >
      <section className="panel stack">
        <h3>Biezace ustawienia</h3>
        {settings ? (
          <pre>{JSON.stringify(settings, null, 2)}</pre>
        ) : (
          <p className="muted">Backend nie odpowiada albo ustawienia nie zostaly jeszcze zapisane.</p>
        )}
      </section>
    </AppShell>
  );
}

