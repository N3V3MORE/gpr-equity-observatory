import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "GPR Equity Observatory",
  description:
    "A research observatory studying whether geopolitical risk helps explain or rank downside risk in international equity markets.",
  icons: {
    icon: "/icon.svg",
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
