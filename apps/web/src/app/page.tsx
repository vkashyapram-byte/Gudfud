import Link from "next/link";
import ScoreChart from "@/components/ScoreChart";

export default async function HomePage() {

  // Native form submission is used for search to ensure it is independent and always works.
  return (
    <div className="min-h-screen bg-brand-surface text-brand-neutral font-mono selection:bg-brand-neutral selection:text-brand-surface">
      <header className="border-b border-brand-border p-6 flex justify-between items-center bg-white">
        <div>
          <h1 className="text-3xl font-bold uppercase tracking-tighter">Gud Fud</h1>
          <p className="text-sm mt-1 uppercase tracking-widest text-brand-neutral/70">
            Transparent Food Label Analysis
          </p>
        </div>
      </header>

      <section className="py-20 px-6 flex flex-col items-center justify-center border-b border-brand-border bg-white">
        <div className="w-full max-w-3xl z-10">
          <form action="/search" method="GET" className="flex items-center w-full border border-brand-border bg-white p-2">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-brand-neutral ml-2 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            <input
              type="text"
              name="q"
              placeholder="Search products, brands, e-numbers..."
              required
              minLength={2}
              className="w-full p-3 text-lg outline-none text-brand-neutral placeholder:text-brand-neutral/50 bg-transparent"
            />
          </form>
          
          <div className="mt-8 flex justify-center">
            <Link
              href="/catalogue"
              className="text-sm uppercase font-bold border border-brand-border px-8 py-3 bg-brand-neutral text-brand-surface hover:bg-brand-neutral/80 transition-none"
            >
              Explore Catalogue
            </Link>
          </div>
        </div>
      </section>

      <main className="p-6 max-w-5xl mx-auto">
        <div className="mb-8 border-b border-brand-border pb-4 flex justify-between items-end">
          <h2 className="text-2xl font-bold uppercase tracking-tight">How We Grade</h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 items-center">
          <div className="space-y-6">
            <p className="text-lg leading-relaxed border border-brand-border p-6 bg-white shadow-sm">
              Gud Fud is an independent AI platform that deeply analyzes food products based on a rigorous 100-point scale. We evaluate every product transparently using a standardized engine.
            </p>
            <div className="space-y-4">
              <div className="border border-brand-border p-4 bg-brand-neutral/5">
                <h3 className="font-bold uppercase mb-2">1. Nutrition (50%)</h3>
                <p className="text-sm">We assess calories, macronutrients, sodium, and sugars against recommended limits.</p>
              </div>
              <div className="border border-brand-border p-4 bg-brand-neutral/5">
                <h3 className="font-bold uppercase mb-2">2. Formulation (30%)</h3>
                <p className="text-sm">We parse every additive, preservative, and raw material, penalizing harmful components and ensuring limits aren't exceeded.</p>
              </div>
              <div className="border border-brand-border p-4 bg-brand-neutral/5">
                <h3 className="font-bold uppercase mb-2">3. Context (20%)</h3>
                <p className="text-sm">We map products into the NOVA framework, rewarding unprocessed foods and penalizing ultra-processed alternatives.</p>
              </div>
            </div>
          </div>
          
          <div className="w-full flex justify-center">
            <ScoreChart />
          </div>
        </div>
      </main>
    </div>
  );
}
