import Link from "next/link";

export default function TeamPage() {
  return (
    <main className="max-w-5xl mx-auto p-8 text-brand-neutral bg-brand-surface min-h-screen">
      <header className="mb-8 border-b border-brand-border pb-6 flex justify-between items-baseline">
        <h1 className="text-3xl font-bold tracking-tight">Team</h1>
        <Link href="/" className="text-sm hover:underline font-medium">Home</Link>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-12">
        <div className="border border-brand-border bg-white p-6">
          <div className="w-24 h-24 bg-brand-surface border border-brand-border mb-4"></div>
          <h2 className="text-xl font-bold mb-1">Jane Doe</h2>
          <p className="text-sm font-mono mb-4 text-gray-700">Founder & Managing Editor</p>
          <p className="text-sm leading-relaxed">
            Jane oversees the editorial integrity and methodology of Gud Fud. Prior to founding the organization, she spent 10 years as a regulatory compliance specialist analyzing food label claims across global markets.
          </p>
        </div>

        <div className="border border-brand-border bg-white p-6">
          <div className="w-24 h-24 bg-brand-surface border border-brand-border mb-4"></div>
          <h2 className="text-xl font-bold mb-1">John Smith</h2>
          <p className="text-sm font-mono mb-4 text-gray-700">Lead Analyst</p>
          <p className="text-sm leading-relaxed">
            John manages the data ingestion and transcription pipeline. His background is in data science and nutritional epidemiology, ensuring structural consistency across the ingredient analysis database.
          </p>
        </div>
      </div>

      <section className="border-t-2 border-brand-neutral pt-8">
        <h2 className="text-2xl font-bold mb-4">Conflict of Interest Policy</h2>
        <div className="border border-brand-border bg-white p-6 space-y-4 text-sm leading-relaxed">
          <p>
            Gud Fud enforces a strict conflict of interest policy to maintain editorial independence and analytical integrity. 
          </p>
          <ul className="list-disc list-inside space-y-2">
            <li>No team member or contributor may hold direct equity, receive compensation, or accept gifts from the food manufacturers, ingredient suppliers, or brands reviewed in our catalogue.</li>
            <li>We do not accept paid placements, sponsored reviews, or "fast-track" analysis requests.</li>
            <li>All corrections or methodology updates are logged publicly via our editorial transparency workflow.</li>
          </ul>
        </div>
      </section>
    </main>
  );
}
