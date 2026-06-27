interface DetailsProps {
  summary: string;
  children: React.ReactNode;
  defaultOpen?: boolean;
}

export function Details({ summary, children, defaultOpen = false }: DetailsProps) {
  return (
    <details
      className="group rounded-lg border border-surface-border bg-surface p-3 shadow-sm open:bg-surface-alt/60"
      open={defaultOpen}
    >
      <summary className="cursor-pointer select-none text-sm font-semibold text-ink-soft marker:text-ink-muted">
        {summary}
      </summary>
      <div className="mt-3 space-y-4 text-sm text-ink-soft">{children}</div>
    </details>
  );
}
