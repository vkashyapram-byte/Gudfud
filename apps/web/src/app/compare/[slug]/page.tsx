import Link from "next/link";
import { notFound } from "next/navigation";

interface VariantComparison {
  market_code: string;
  label_version_id: string;
  local_name: string | null;
  serving_quantity: number | null;
  serving_unit: string | null;
  methodology_version: string;
  nutrition: { energy: number; fat: number; sugars: number; sodium: number; protein: number } | null;
  ingredients: Array<{ label_text: string; position: number }>;
}

interface ComparisonData {
  slug: string;
  canonical_name: string;
  brand_name: string;
  variants: VariantComparison[];
}

async function getComparison(slug: string, markets: string): Promise<ComparisonData | null> {
  try {
    const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/v1/compare/${slug}?markets=${markets}`, { cache: "no-store" });
    if (!res.ok) return null;
    return res.json();
  } catch (error) {
    return null;
  }
}

export default async function ComparePage({ params, searchParams }: { params: { slug: string }, searchParams: { [key: string]: string | string[] | undefined } }) {
  const marketsStr = typeof searchParams.markets === 'string' ? searchParams.markets : "IN";
  const data = await getComparison(params.slug, marketsStr);

  if (!data || data.variants.length === 0) notFound();

  return (
    <main className="max-w-6xl mx-auto p-8 text-brand-neutral bg-brand-surface min-h-screen">
      <header className="mb-8 border-b border-brand-border pb-6">
        <Link href={`/products/${data.slug}`} className="text-sm hover:underline mb-4 inline-block font-medium">&lt; Back to Product</Link>
        <h1 className="text-3xl font-bold tracking-tight mb-1">{data.canonical_name} - Market Comparison</h1>
        <p className="text-sm font-semibold">{data.brand_name}</p>
      </header>

      <div className="flex overflow-x-auto pb-4 gap-6">
        {data.variants.map((v) => (
          <div key={v.market_code} className="min-w-[300px] flex-1 border border-brand-border bg-white flex flex-col">
            <div className="bg-brand-neutral text-brand-surface p-4 font-bold text-lg flex justify-between items-center">
              {v.local_name || data.canonical_name}
              <span className="font-mono text-sm border border-brand-surface px-1">{v.market_code}</span>
            </div>
            
            <div className="p-4 border-b border-brand-border text-sm bg-brand-surface">
              <p><strong>Methodology:</strong> {v.methodology_version}</p>
              <p><strong>Serving:</strong> {v.serving_quantity ? `${v.serving_quantity} ${v.serving_unit}` : "N/A"}</p>
            </div>

            <div className="p-4 flex-1">
              <h3 className="font-semibold border-b border-brand-border pb-1 mb-3 text-sm">Normalized Nutrition (per 100g/ml)</h3>
              {v.nutrition ? (
                <ul className="text-sm space-y-2 mb-6">
                  <li className="flex justify-between"><span>Energy</span> <span className="font-mono">{v.nutrition.energy ?? "-"}</span></li>
                  <li className="flex justify-between"><span>Sugars</span> <span className="font-mono">{v.nutrition.sugars ?? "-"}</span></li>
                  <li className="flex justify-between"><span>Sodium</span> <span className="font-mono">{v.nutrition.sodium ?? "-"}</span></li>
                </ul>
              ) : (
                <p className="text-sm text-gray-600 mb-6">No data</p>
              )}

              <h3 className="font-semibold border-b border-brand-border pb-1 mb-3 text-sm">Ingredient Formulation</h3>
              <ol className="list-decimal list-inside text-sm space-y-1 text-gray-800">
                {v.ingredients.map(ing => (
                  <li key={ing.position} className="pl-1 leading-snug pb-1 border-b border-brand-surface">{ing.label_text}</li>
                ))}
              </ol>
            </div>
          </div>
        ))}
      </div>
    </main>
  );
}
