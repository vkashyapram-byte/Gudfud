import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  metadataBase: new URL(process.env.NEXT_PUBLIC_SITE_URL || "http://localhost:3000"),
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
