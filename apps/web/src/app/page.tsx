import Link from "next/link";
import { redirect } from "next/navigation";
import ScoreChart from "@/components/ScoreChart";

export default async function HomePage() {

  async function search(formData: FormData) {
    "use server";
    const query = formData.get("q");
    if (query && typeof query === "string" && query.length >= 2) {
      redirect(`/search?q=${encodeURIComponent(query)}`);
    }
  }

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

      <section className="py-24 px-6 flex flex-col items-center justify-center bg-brand-surface border-b border-brand-border">
        <div className="w-full max-w-3xl z-10 flex flex-col items-center">
          <form action={search} className="flex items-center w-full bg-white rounded-full shadow-lg p-3 border-2 border-brand-neutral/10 focus-within:border-[#4ECDC4] transition-colors">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-brand-neutral ml-4 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            <input
              type="text"
              name="q"
              placeholder="Search products, brands, e-numbers..."
              required
              minLength={2}
              className="w-full px-4 py-2 text-xl outline-none text-brand-neutral placeholder:text-brand-neutral/40 bg-transparent font-sans"
            />
            <button type="submit" className="bg-[#FF6B6B] text-white px-6 py-2 rounded-full font-bold hover:bg-[#ff5252] transition-colors shadow-sm">Search</button>
          </form>
          
          <div className="mt-8">
            <Link
              href="/catalogue"
              className="inline-block text-sm uppercase tracking-wider font-bold bg-white text-[#4ECDC4] border-2 border-[#4ECDC4] px-8 py-3 rounded-full hover:bg-[#4ECDC4] hover:text-white transition-all shadow-sm transform hover:-translate-y-1"
            >
              Explore Catalogue
            </Link>
          </div>
        </div>
      </section>

      <main className="p-6 md:p-12 max-w-6xl mx-auto">
        <div className="text-center mb-12">
          <h2 className="text-3xl md:text-5xl font-extrabold tracking-tight mb-4 text-brand-neutral">How We Grade</h2>
          <p className="text-lg text-brand-neutral/70 max-w-2xl mx-auto font-sans">
            Ever wonder what's really in your food? We break it down so you don't have to. Our AI engine scores products on a 100-point scale.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-12">
          <div className="bg-[#FF6B6B]/10 border-2 border-[#FF6B6B]/20 p-8 rounded-3xl flex flex-col items-center text-center transform hover:scale-105 transition-transform">
            <div className="text-5xl mb-4">🥦</div>
            <h3 className="font-bold text-xl mb-3 text-brand-neutral">1. Nutrition (50%)</h3>
            <p className="text-sm font-sans text-brand-neutral/80">We look at the macros! Balancing the good stuff like protein with the things you might want to watch, like sugar and sodium.</p>
          </div>
          
          <div className="bg-[#4ECDC4]/10 border-2 border-[#4ECDC4]/20 p-8 rounded-3xl flex flex-col items-center text-center transform hover:scale-105 transition-transform">
            <div className="text-5xl mb-4">🔬</div>
            <h3 className="font-bold text-xl mb-3 text-brand-neutral">2. Ingredients (30%)</h3>
            <p className="text-sm font-sans text-brand-neutral/80">No more mysterious E-numbers. We scan the label for additives, preservatives, and weird chemicals.</p>
          </div>

          <div className="bg-[#FFE66D]/20 border-2 border-[#FFE66D]/40 p-8 rounded-3xl flex flex-col items-center text-center transform hover:scale-105 transition-transform">
            <div className="text-5xl mb-4">🏭</div>
            <h3 className="font-bold text-xl mb-3 text-brand-neutral">3. Processing (20%)</h3>
            <p className="text-sm font-sans text-brand-neutral/80">Is it real food or a science experiment? We check how processed the product actually is using the NOVA framework.</p>
          </div>
        </div>

        <div className="w-full flex justify-center max-w-2xl mx-auto">
          <ScoreChart />
        </div>
      </main>
    </div>
  );
}
