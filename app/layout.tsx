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
  title: "DPV Offshore | Yacht refit and repair at Galle Port, Sri Lanka",
  description:
    "Hull, engine, electrical, navigation and interior work for yachts calling at Galle Port, Sri Lanka. DPV Offshore Marine Services (Pvt) Ltd.",
  openGraph: {
    title: "DPV Offshore | Yacht refit and repair at Galle Port",
    description: "Hull, engine, electrical, navigation and interior work for yachts calling at Galle, by one accountable team.",
    type: "website",
    locale: "en_GB",
  },
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  viewportFit: "cover",
  themeColor: "#ffffff",
  colorScheme: "light",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={archivo.variable} suppressHydrationWarning>
      <head>
        {/* Hide reveal targets before first paint; Motion removes this for reduced-motion users. */}
        <script
          dangerouslySetInnerHTML={{
            __html: `if(!matchMedia("(prefers-reduced-motion: reduce)").matches)document.documentElement.classList.add("js-motion")`,
          }}
        />
      </head>
      <body>{children}</body>
    </html>
  );
}
