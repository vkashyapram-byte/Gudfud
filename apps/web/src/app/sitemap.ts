import type { MetadataRoute } from 'next';

export default function sitemap(): MetadataRoute.Sitemap {
  let rawSiteUrl = process.env.NEXT_PUBLIC_SITE_URL || process.env.VERCEL_URL || 'http://localhost:3000';
  if (rawSiteUrl.includes("[SENSITIVE]")) {
    rawSiteUrl = 'http://localhost:3000';
  }
  const baseUrl = rawSiteUrl.startsWith("http") ? rawSiteUrl : `https://${rawSiteUrl}`;

  const staticRoutes = [
    '',
    '/catalogue',
    '/how-it-works',
    '/team',
    '/privacy',
    '/terms',
  ].map((route) => ({
    url: `${baseUrl}${route}`,
    lastModified: new Date(),
    changeFrequency: 'weekly' as const,
    priority: route === '' ? 1.0 : 0.8,
  }));

  return [...staticRoutes];
}
