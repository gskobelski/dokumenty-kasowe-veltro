export function ExportPanel() {
  return (
    <section className="panel stack">
      <h3>Eksport EPP</h3>
      <p className="muted">
        Backend generuje plik kompatybilny z Rewizorem GT pod endpointem
        {" "}
        <code>/api/export/epp</code>.
      </p>
      <div className="button-row">
        <a className="button" href="http://localhost:8000/api/export/epp">
          Pobierz .epp
        </a>
      </div>
      <p className="muted">
        Rewizor GT: Narzedzia -&gt; Import -&gt; Plik komunikacji.
      </p>
    </section>
  );
}

