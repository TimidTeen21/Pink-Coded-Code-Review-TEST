// frontend/next.config.ts
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  output: 'standalone', // For Docker optimization
  experimental: {

  },
  pageExtensions: ['tsx', 'ts', 'jsx', 'js'],
};

export default nextConfig;