interface SectionProps {
  id: string;
  eyebrow: string;
  title: string;
  intro?: string;
  children: React.ReactNode;
}

export function Section({ id, eyebrow, title, intro, children }: SectionProps) {
  return (
    <section id={id} className="scroll-mt-16 py-10 sm:py-12">
      <div className="mx-auto max-w-6xl px-4">
        <p className="text-xs font-semibold uppercase tracking-wider text-accent">{eyebrow}</p>
        <h2 className="mt-1 text-2xl font-semibold text-ink sm:text-3xl">{title}</h2>
        {intro ? <p className="mt-2 max-w-3xl text-sm text-ink-soft">{intro}</p> : null}
        <div className="mt-6 space-y-6">{children}</div>
      </div>
    </section>
  );
}
