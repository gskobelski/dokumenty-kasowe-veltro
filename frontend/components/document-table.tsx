import type { CashDocument } from "./types";

export function DocumentTable({ documents }: { documents: CashDocument[] }) {
  return (
    <div className="panel">
      <div className="button-row">
        <span className="tag">{documents.length} rekordow</span>
      </div>
      <table className="table">
        <thead>
          <tr>
            <th>Typ</th>
            <th>Data</th>
            <th>Kwota</th>
            <th>Zrodlo</th>
            <th>Odbiorca</th>
            <th>Walidacja</th>
            <th>Tytul</th>
          </tr>
        </thead>
        <tbody>
          {documents.map((document) => (
            <tr key={document.id}>
              <td>{document.document_type}</td>
              <td>{document.issue_date}</td>
              <td>{document.amount}</td>
              <td>{document.source_type}</td>
              <td>{document.recipient_name_full || document.recipient_name_short}</td>
              <td>{document.validation_status}</td>
              <td>{document.title}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

