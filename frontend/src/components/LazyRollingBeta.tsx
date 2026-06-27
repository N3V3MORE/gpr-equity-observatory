"use client";

import { useEffect, useRef, useState } from "react";

import { RollingBetaChart } from "@/components/charts";
import { loadRollingBeta } from "@/lib/data";
import type { Row } from "@/lib/types";

export function LazyRollingBeta() {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const [shouldLoad, setShouldLoad] = useState(false);
  const [rows, setRows] = useState<Row[] | null>(null);

  useEffect(() => {
    const node = containerRef.current;
    if (!node || shouldLoad) return;

    if (!("IntersectionObserver" in window)) {
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
  }, [shouldLoad]);

  useEffect(() => {
    if (!shouldLoad) return;

    let active = true;
    loadRollingBeta().then((data) => {
      if (active) setRows(data);
    });
    return () => {
      active = false;
    };
  }, [shouldLoad]);

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

  if (rows.length === 0) {
    return (
      <div ref={containerRef} className="text-sm text-ink-muted">
        No rolling-sensitivity data available.
      </div>
    );
  }

  return (
    <div ref={containerRef}>
      <RollingBetaChart rows={rows} />
    </div>
  );
}
