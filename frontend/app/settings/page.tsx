import { AppShell } from "../../components/app-shell";
import { SettingsForm } from "../../components/settings-form";
import { getSettings } from "../../lib/api";

export default async function SettingsPage() {
  const settings = await getSettings().catch(() => null);

  return (
    <AppShell
      title="Ustawienia podstawowe"
      subtitle="Dane firmy, kasy i stalego podmiotu bankowego wykorzystywane w eksporcie EPP."
    >
      <SettingsForm initialSettings={settings} />
    </AppShell>
  );
}
