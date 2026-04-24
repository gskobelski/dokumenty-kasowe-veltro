import Link from "next/link";
import type { ReactNode } from "react";

export function AppShell({
  title,
  subtitle,
  children,
}: {
  title: string;
  subtitle: string;
  children: ReactNode;
}) {
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <p className="eyebrow">Veltro</p>
        <h1 className="brand">Dokumenty kasowe KP/KW</h1>
        <nav className="nav">
          <Link href="/">Dashboard</Link>
          <Link href="/import">Import</Link>
          <Link href="/documents">Dokumenty</Link>
          <Link href="/settings">Ustawienia</Link>
        </nav>
      </aside>
      <main className="content">
        <header className="page-header">
          <div className="hero">
            <span className="eyebrow">MVP</span>
            <h2>{title}</h2>
            <p className="muted">{subtitle}</p>
          </div>
        </header>
        {children}
      </main>
    </div>
  );
}

