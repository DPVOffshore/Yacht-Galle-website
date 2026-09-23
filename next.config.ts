import type { NextConfig } from "next";

// Set by the GitHub Pages workflow (e.g. "/Yacht-Galle-website"). Builds a static export under that sub-path.
const basePath = process.env.NEXT_PUBLIC_BASE_PATH ?? "";
const staticExport = process.env.STATIC_EXPORT === "true";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  ...(staticExport
    ? {
        output: "export",
        basePath: basePath || undefined,
        images: { unoptimized: true },
      }
    : {
        async headers() {
          return [
            {
              // The 3D model is large; let browsers and CDNs cache it for a day.
              source: "/models/:path*",
              headers: [{ key: "Cache-Control", value: "public, max-age=86400, stale-while-revalidate=604800" }],
            },
          ];
        },
      }),
};

export default nextConfig;
