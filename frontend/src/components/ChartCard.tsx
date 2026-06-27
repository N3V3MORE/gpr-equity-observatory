interface ChartCardProps {
  title: string;
  caption?: string;
  children: React.ReactNode;
}

export function ChartCard({ title, caption, children }: ChartCardProps) {
  return (
    <div className="rounded-lg border border-surface-border bg-surface p-4 shadow-sm">
      <h4 className="text-sm font-semibold text-ink">{title}</h4>
      <div className="mt-3">{children}</div>
      {caption ? <p className="mt-3 text-xs text-ink-muted">{caption}</p> : null}
    </div>
  );
}
