import type { NextConfig } from "next";

const apiUrl = process.env.NEXT_PUBLIC_API_URL 
  || (process.env.VERCEL_PROJECT_PRODUCTION_URL ? `https://${process.env.VERCEL_PROJECT_PRODUCTION_URL}` : null)
  || (process.env.VERCEL_URL ? `https://${process.env.VERCEL_URL}` : "http://127.0.0.1:8000");

const nextConfig: NextConfig = {
  env: {
    NEXT_PUBLIC_API_URL: apiUrl
  }
};

export default nextConfig;
