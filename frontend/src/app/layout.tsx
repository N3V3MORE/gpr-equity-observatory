import type { Metadata } from "next";
import { publicPath } from "@/lib/paths";
import "./globals.css";

export const metadata: Metadata = {
  title: "GPR Equity Observatory",
  description:
    "Daily geopolitical risk and developed and emerging equity markets: snapshot-backed event-study and panel-regression evidence, methods, data coverage, and limitations.",
  icons: { shortcut: publicPath("icon.svg") },
  openGraph: {
    title: "GPR Equity Observatory",
    description: "Research on geopolitical risk and country ETF returns. Associations, uncertainty, and limitations alongside the evidence.",
    type: "website",
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" data-scroll-behavior="smooth">
      <body>{children}</body>
    </html>
  );
}
