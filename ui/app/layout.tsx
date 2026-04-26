import "./globals.css";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Compensation Equity Analyzer",
  description: "Blinder-Oaxaca decomposition for pay-equity audits",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
