import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "CellSentry",
  description: "Battery supply-chain risk & traceability intelligence",
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
