import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "standalone",
  // basePath is set at build time via env var so the same image can serve
  // at / (local dev) or /chat (production behind nginx).
  basePath: process.env.NEXT_PUBLIC_BASE_PATH ?? "",
};

export default nextConfig;
