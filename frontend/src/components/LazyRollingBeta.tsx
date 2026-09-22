"use client";

import { useEffect, useRef, useState } from "react";

import { RollingBetaChart } from "@/components/charts";
import { loadRollingBeta } from "@/lib/data";
import type { DatasetStatus, Manifest, Row } from "@/lib/types";

export function LazyRollingBeta({ manifest, status }: { manifest: Manifest; status: DatasetStatus }) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const [shouldLoad, setShouldLoad] = useState(false);
  const [rows, setRows] = useState<Row[] | null>(null);
  const [unavailable, setUnavailable] = useState(false);
  const canLoad = status === "deferred" || status === "available";

  useEffect(() => {
    const node = containerRef.current;
    if (!node || shouldLoad || !canLoad) return;

    if (!("IntersectionObserver" in window)) {
      // Preserve immediate loading in browsers without IntersectionObserver.
      // eslint-disable-next-line react-hooks/set-state-in-effect
      setShouldLoad(true);
      return;
    }

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setShouldLoad(true);
          observer.disconnect();
        }
      },
      { rootMargin: "240px" },
    );

    observer.observe(node);
    return () => observer.disconnect();
  }, [shouldLoad, canLoad]);

  useEffect(() => {
    if (!shouldLoad || !canLoad) return;

    let active = true;
    loadRollingBeta(manifest)
      .then((data) => {
        if (!active) return;
        if (data === null || data.length === 0) setUnavailable(true);
        else setRows(data);
      })
      .catch(() => {
        if (active) setUnavailable(true);
      });
    return () => {
      active = false;
    };
  }, [shouldLoad, canLoad, manifest]);

  if (status === "excluded") return null;

  if (status === "unavailable" || unavailable) {
    return <p role="status" className="text-sm text-ink-muted">Country sensitivity is unavailable in this snapshot.</p>;
  }

  if (!shouldLoad) {
    return (
      <div ref={containerRef} className="text-sm text-ink-muted">
        Country sensitivity data will load when this section is in view.
      </div>
    );
  }

  if (rows === null) {
    return (
      <div ref={containerRef} className="text-sm text-ink-muted">
        Loading sensitivity data...
      </div>
    );
  }

  return (
    <div ref={containerRef}>
      <RollingBetaChart rows={rows} />
    </div>
  );
}
