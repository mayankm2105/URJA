import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "FleetMind — EV Battery Asset War-Room",
  description:
    "Battery State-of-Health, remaining-useful-life and predictive maintenance for EV fleets.",
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
