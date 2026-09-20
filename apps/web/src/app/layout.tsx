import type { Metadata } from "next";
import "./globals.css";

const rawSiteUrl = process.env.NEXT_PUBLIC_SITE_URL || process.env.VERCEL_URL || "localhost:3000";
const siteUrl = rawSiteUrl.startsWith("http") ? rawSiteUrl : `https://${rawSiteUrl}`;

export const metadata: Metadata = {
  metadataBase: new URL(siteUrl),
  title: "Gud Fud | Transparent Food Label Analysis",
  description: "Public catalogue and analysis of food product formulations, nutritional data, and ingredient evidence.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="text-brand-neutral bg-brand-surface font-sans antialiased selection:bg-brand-neutral selection:text-white">
        {children}
      </body>
    </html>
  );
}
