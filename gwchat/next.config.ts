import type { NextConfig } from "next";

const basePath = process.env.NEXT_PUBLIC_BASE_PATH ?? "";

const nextConfig: NextConfig = {
  output: "standalone",
  // basePath is set at build time via env var so the same image can serve
  // at / (local dev) or /chat (production behind nginx).
  basePath: basePath || undefined,
  // Direct hits to http://host:3000/ would otherwise 404 when basePath is set.
  async redirects() {
    if (!basePath) {
      return [];
    }
    return [
      {
        source: "/",
        destination: basePath,
        permanent: false,
        basePath: false,
      },
    ];
  },
};

export default nextConfig;
