interface GlossaryProps {
  terms: Record<string, string>;
}

export function Glossary({ terms }: GlossaryProps) {
  const entries = Object.entries(terms);
  if (entries.length === 0) return null;
  return (
    <dl className="grid gap-4 sm:grid-cols-2">
      {entries.map(([term, explanation]) => (
        <div key={term} className="rounded-lg border border-surface-border bg-surface p-3">
          <dt className="text-sm font-semibold text-ink">{term}</dt>
          <dd className="mt-1 text-sm text-ink-soft">{explanation}</dd>
        </div>
      ))}
    </dl>
  );
}
