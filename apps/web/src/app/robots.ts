import type { MetadataRoute } from 'next';

export default function robots(): MetadataRoute.Robots {
  let rawSiteUrl = process.env.NEXT_PUBLIC_SITE_URL || process.env.VERCEL_URL || 'http://localhost:3000';
  if (rawSiteUrl.includes("[SENSITIVE]")) {
    rawSiteUrl = 'http://localhost:3000';
  }
  const baseUrl = rawSiteUrl.startsWith("http") ? rawSiteUrl : `https://${rawSiteUrl}`;

  return {
    rules: {
      userAgent: '*',
      allow: '/',
      disallow: ['/admin', '/api/'],
    },
    sitemap: `${baseUrl}/sitemap.xml`,
  };
}
