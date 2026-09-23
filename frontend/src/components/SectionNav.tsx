const SECTIONS = [
  { id: "overview", label: "Current answer" },
  { id: "how-markets-react", label: "Key evidence" },
  { id: "prediction-lab", label: "Prediction Lab" },
  { id: "country-sensitivity", label: "Country sensitivity" },
  { id: "data-and-methods", label: "Methods & data" },
];

export function SectionNav({ prediction = false, rolling = false }: { prediction?: boolean; rolling?: boolean }) {
  return (
    <nav aria-label="Research sections" className="sticky top-0 z-10 overflow-x-hidden border-b border-surface-border bg-surface/90 backdrop-blur">
      <div className="mx-auto flex w-full max-w-full gap-1 overflow-x-auto px-4 py-2 text-sm lg:max-w-6xl">
        {SECTIONS.filter((section) =>
          (section.id !== "prediction-lab" || prediction) &&
          (section.id !== "country-sensitivity" || rolling),
        ).map((section) => (
          <a
            key={section.id}
            href={`#${section.id}`}
            className="whitespace-nowrap rounded px-3 py-1.5 font-medium text-ink-soft hover:bg-accent-soft hover:text-accent focus:outline-none focus:ring-2 focus:ring-accent/30"
          >
            {section.label}
          </a>
        ))}
      </div>
    </nav>
  );
}
