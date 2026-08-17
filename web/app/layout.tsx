import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Wind Calculator",
  description: "Engineering wind-load calculator for the approved WIND-DUAL-001 specification.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
