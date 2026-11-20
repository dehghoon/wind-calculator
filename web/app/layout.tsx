import { createElement } from "react";
import type { Metadata } from "next";
import "./globals.css";
import "./linkoteq-theme.css";

export const metadata: Metadata = {
  title: "Wind Load Calculator | Linkoteq",
  description: "Engineering wind-load calculator for the approved WIND-DUAL-001 specification.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en" data-linkoteq-surface="wind">
      <head>
        <script defer src="https://www.linkoteq.com/design-system/linkoteq-header-v1.js" />
      </head>
      <body>{createElement("linkoteq-header")}{children}</body>
    </html>
  );
}
