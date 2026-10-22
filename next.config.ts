import type { NextConfig } from "next";

// Set by the GitHub Pages workflow: builds a static export served from the root of yachtclubgalle.com.
const staticExport = process.env.STATIC_EXPORT === "true";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  trailingSlash: true,
  ...(staticExport
    ? {
        output: "export",
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
