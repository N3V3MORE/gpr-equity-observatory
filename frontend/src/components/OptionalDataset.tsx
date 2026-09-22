import type { DatasetStatus } from "@/lib/types";

export function OptionalDataset({
  status,
  label,
  children,
}: {
  status: DatasetStatus;
  label: string;
  children: React.ReactNode;
}) {
  if (status === "excluded") return null;
  if (status === "unavailable") {
    return <p role="status" className="text-sm text-ink-muted">{label} is unavailable in this snapshot.</p>;
  }
  return children;
}
