type Variant = "info" | "warning" | "danger";

interface CalloutProps {
  variant?: Variant;
  title?: string;
  children: React.ReactNode;
}

const STYLES: Record<Variant, { box: string; title: string }> = {
  info: { box: "border-accent/30 bg-accent-soft text-ink", title: "text-accent" },
  warning: { box: "border-amber-300 bg-amber-50 text-ink", title: "text-amber-700" },
  danger: { box: "border-rose-300 bg-rose-50 text-ink", title: "text-rose-700" },
};

export function Callout({ variant = "info", title, children }: CalloutProps) {
  const style = STYLES[variant];
  return (
    <div className={`rounded-lg border px-4 py-3 text-sm shadow-sm ${style.box}`}>
      {title ? <div className={`mb-1 font-semibold ${style.title}`}>{title}</div> : null}
      <div className="leading-relaxed">{children}</div>
    </div>
  );
}
