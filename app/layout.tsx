import type { Metadata, Viewport } from "next";
import localFont from "next/font/local";
import "./globals.css";

// Archivo variable font (width 62–125%, weight 100–900), self-hosted. Licence: app/fonts/LICENSE-Archivo-OFL.txt
const archivo = localFont({
  src: [{ path: "./fonts/archivo-latin-wdth-normal.woff2", weight: "100 900", style: "normal" }],
  variable: "--font-archivo",
  display: "swap",
  declarations: [{ prop: "font-stretch", value: "62% 125%" }],
  fallback: ["Helvetica Neue", "Helvetica", "Arial", "sans-serif"],
});

export const metadata: Metadata = {
  metadataBase: new URL(process.env.NEXT_PUBLIC_SITE_URL ?? "http://localhost:3000"),
  title: "Yacht Club Galle | A New Perspective on Life at Sea",
  description:
    "Discover the Yacht Club Galle vision: yacht care, marine expertise and international club connections on Sri Lanka’s southern coast.",
  openGraph: {
    title: "Yacht Club Galle | A New Perspective on Life at Sea",
    description: "A new chapter in yachting at Galle. Discover our vision for owners, captains and international yacht clubs.",
    images: [{ url: "/web/01-yacht-at-anchor.webp", width: 1672, height: 941, alt: "Yacht Club Galle — a new horizon in Sri Lanka" }],
    type: "website",
    locale: "en_GB",
  },
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  viewportFit: "cover",
  themeColor: "#f6f4ef",
  colorScheme: "light",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={archivo.variable} data-scroll-behavior="smooth">
      <body>{children}</body>
    </html>
  );
}
