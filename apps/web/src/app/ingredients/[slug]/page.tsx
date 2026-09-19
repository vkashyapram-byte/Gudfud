import Link from "next/link";
import { notFound } from "next/navigation";

interface Source {
  title: string;
  publisher: string;
  url: string | null;
  publication_date: string | null;
}

interface Evidence {
  effect_type: string;
  population: string | null;
  dose_context: string | null;
  evidence_grade: string;
  summary: string;
  jurisdiction: string | null;
  sources: Source[];
}

interface RegulatoryStatus {
  market_code: string;
  status: string;
  use_category: string;
  conditions: string | null;
  max_level: string | null;
  effective_from: string;
  source: Source | null;
}

interface IngredientAnalysis {
  slug: string;
  canonical_name: string;
  INS_number: string | null;
  E_number: string | null;
  ingredient_type: string | null;
  technical_function: string | null;
  public_summary: string | null;
  aliases: string[];
  evidence: Evidence[];
  regulatory_statuses: RegulatoryStatus[];
  products: Array<{ slug: string; canonical_name: string; brand_name: string; rating_band: string | null }>;
}

async function getIngredient(slug: string): Promise<IngredientAnalysis | null> {
  try {
    const res = await fetch(`http://127.0.0.1:8000/v1/ingredients/${slug}`, { cache: "no-store" });
    if (!res.ok) return null;
    return res.json();
  } catch (error) {
    return null;
  }
}

export default async function IngredientPage({ params }: { params: { slug: string } }) {
  const ingredient = await getIngredient(params.slug);
  
  if (!ingredient) notFound();

  return (
    <main className="max-w-5xl mx-auto p-8 text-brand-neutral bg-brand-surface min-h-screen">
      <header className="mb-8 border-b border-brand-border pb-6">
        <Link href="/" className="text-sm hover:underline mb-4 inline-block font-medium">&lt; Back to Search</Link>
        <h1 className="text-3xl font-bold tracking-tight mb-2">{ingredient.canonical_name}</h1>
        <div className="flex gap-4 text-sm font-mono uppercase bg-white border border-brand-border p-3 inline-flex">
          {ingredient.INS_number && <span>INS: {ingredient.INS_number}</span>}
          {ingredient.E_number && <span>E: {ingredient.E_number}</span>}
          <span>Type: {ingredient.ingredient_type || "N/A"}</span>
        </div>
      </header>

      <section className="mb-8 border border-brand-border p-6 bg-white">
        <h2 className="text-xl font-semibold mb-2 border-b border-brand-border pb-2">Function & Summary</h2>
        <p className="text-sm font-semibold mb-2 text-gray-800">Purpose: {ingredient.technical_function || "Not declared"}</p>
        <p className="text-sm leading-relaxed">{ingredient.public_summary || "No summary available."}</p>
        {ingredient.aliases.length > 0 && (
          <p className="text-xs mt-4 text-gray-600">Also known as: {ingredient.aliases.join(", ")}</p>
        )}
      </section>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <section className="space-y-6">
          <h2 className="text-xl font-semibold border-b border-brand-border pb-2">Evidence & Effects</h2>
          {ingredient.evidence.length === 0 ? (
            <p className="text-sm border border-brand-border p-4 bg-white">No specific health evidence logged.</p>
          ) : (
            ingredient.evidence.map((ev, idx) => (
              <div key={idx} className="border border-brand-border p-5 bg-white space-y-3 text-sm">
                <div className="flex justify-between items-start font-bold">
                  <h3>{ev.effect_type}</h3>
                  <span className="uppercase text-xs border border-brand-neutral px-1">{ev.evidence_grade}</span>
                </div>
                <p className="text-gray-800">{ev.summary}</p>
                {(ev.population || ev.dose_context) && (
                  <div className="bg-brand-surface p-3 border border-brand-border text-xs space-y-1">
                    {ev.population && <p><strong>Sensitive group:</strong> {ev.population}</p>}
                    {ev.dose_context && <p><strong>Dose context:</strong> {ev.dose_context}</p>}
                  </div>
                )}
                <ul className="text-xs text-gray-600 space-y-1 pt-2 border-t border-brand-border">
                  {ev.sources.map((src, sIdx) => (
                    <li key={sIdx}>Source: {src.url ? <a href={src.url} className="underline hover:text-brand-neutral">{src.title}</a> : src.title} ({src.publisher})</li>
                  ))}
                </ul>
              </div>
            ))
          )}
        </section>

        <section className="space-y-6">
          <h2 className="text-xl font-semibold border-b border-brand-border pb-2">Regulatory Context</h2>
          {ingredient.regulatory_statuses.length === 0 ? (
            <p className="text-sm border border-brand-border p-4 bg-white">No regulatory data logged.</p>
          ) : (
            ingredient.regulatory_statuses.map((reg, idx) => (
              <div key={idx} className="border border-brand-border p-5 bg-white text-sm space-y-2">
                <div className="flex justify-between items-center font-bold mb-1">
                  <span className="uppercase">{reg.market_code}</span>
                  <span className="bg-brand-surface border border-brand-border px-2 py-0.5">{reg.status}</span>
                </div>
                <p><strong>Category:</strong> {reg.use_category}</p>
                {reg.max_level && <p><strong>Max Level:</strong> {reg.max_level}</p>}
                {reg.conditions && <p><strong>Conditions:</strong> {reg.conditions}</p>}
                <p className="text-xs text-gray-600 mt-2">Effective: {new Date(reg.effective_from).toLocaleDateString()}</p>
              </div>
            ))
          )}
        </section>
      </div>

      <section className="mt-12">
        <h2 className="text-xl font-semibold border-b border-brand-border pb-2 mb-6">Products Containing This Ingredient</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {ingredient.products.map(p => (
            <Link key={p.slug} href={`/products/${p.slug}`} className="block border border-brand-border p-4 bg-white hover:border-brand-neutral transition-colors text-sm">
              <span className="font-bold block">{p.canonical_name}</span>
              <span className="text-gray-600 block">{p.brand_name}</span>
            </Link>
          ))}
        </div>
      </section>
    </main>
  );
}
