import Link from "next/link";

export default function HowItWorksPage() {
  return (
    <main className="max-w-4xl mx-auto p-8 text-brand-neutral bg-brand-surface min-h-screen">
      <header className="mb-8 border-b border-brand-border pb-6 flex justify-between items-baseline">
        <h1 className="text-3xl font-bold tracking-tight">How it Works</h1>
        <Link href="/" className="text-sm hover:underline font-medium">Home</Link>
      </header>

      <section className="space-y-8">
        <div className="border border-brand-border bg-white p-6 flex gap-6">
          <div className="font-mono text-3xl font-bold text-gray-400">01</div>
          <div>
            <h2 className="text-xl font-bold mb-2">Data Collection</h2>
            <p className="text-sm leading-relaxed text-gray-800">
              We source product label data directly from the physical packaging available in distinct consumer markets. We do not rely on marketing copy or press releases. The package formulation is captured, dated, and logged against a specific market code (e.g., IN, US, EU) to track regional variations.
            </p>
          </div>
        </div>

        <div className="border border-brand-border bg-white p-6 flex gap-6">
          <div className="font-mono text-3xl font-bold text-gray-400">02</div>
          <div>
            <h2 className="text-xl font-bold mb-2">Transcription & Normalization</h2>
            <p className="text-sm leading-relaxed text-gray-800">
              The ingredient list and nutritional facts are transcribed into our structured database. All nutritional values are mathematically normalized to standard units (per 100g or 100ml) to ensure accurate side-by-side market comparison. Ingredients are mapped to standardized biological and chemical identifiers (such as INS or E numbers).
            </p>
          </div>
        </div>

        <div className="border border-brand-border bg-white p-6 flex gap-6">
          <div className="font-mono text-3xl font-bold text-gray-400">03</div>
          <div>
            <h2 className="text-xl font-bold mb-2">Review & Publication</h2>
            <p className="text-sm leading-relaxed text-gray-800">
              Once transcription is complete, the product version is evaluated against our methodology engine. Health evidence and regulatory statuses linked to the ingredients are compiled. A final review is conducted by our editorial team before the label version is committed to the public catalogue via an atomic database transaction.
            </p>
          </div>
        </div>
      </section>
    </main>
  );
}
