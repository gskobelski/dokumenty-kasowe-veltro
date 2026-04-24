"use client";

import { useState } from "react";

export function DocumentEditor() {
  const [message, setMessage] = useState(
    "Edycja rekordu odbywa sie przez PATCH /api/documents/{id}. Interfejs jest przygotowany pod kolejne iteracje.",
  );

  return (
    <section className="panel stack">
      <h3>Edycja rekordu</h3>
      <p className="muted">{message}</p>
      <div className="field">
        <label htmlFor="editor-note">Notatka operatora</label>
        <textarea
          id="editor-note"
          rows={5}
          onChange={(event) => setMessage(event.target.value)}
          defaultValue={message}
        />
      </div>
    </section>
  );
}

