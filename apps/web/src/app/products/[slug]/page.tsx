import Link from "next/link";
import { notFound } from "next/navigation";
import { getApiUrl } from "@/lib/api";

interface IngredientMapping {
  label_text: string;
  position: number;
  canonical_name: string | null;
  slug: string | null;
}

interface NutritionFacts {
  energy: number | null;
  fat: number | null;
  saturated_fat: number | null;
  sugars: number | null;
  sodium: number | null;
}

interface ProductAnalysis {
  slug: string;
  canonical_name: string;
  brand_name: string;
  market_code: string;
  rating_total: number | null;
  rating_band: string | null;
  confidence_grade: string;
  explanation: any;
  nutrition: NutritionFacts | null;
  ingredients: IngredientMapping[];
  image_url: string | null;
  last_reviewed_at: string | null;
  methodology_version?: string;
  flags?: { type: string; label: string }[];
  gtin?: string | null;
  component_scores?: {
    nutrition_score: number | null;
    ingredient_score: number | null;
    context_score: number | null;
  };
  sources?: { source_id: string; title: string; url: string; accessed_at: string }[];
}

async function getProduct(slug: string): Promise<ProductAnalysis | null> {
  try {
    const baseUrl = getApiUrl();
    const res = await fetch(`${baseUrl}/v1/products/${slug}`, { cache: "no-store" });
    if (!res.ok) return null;
    return res.json();
  } catch (error) {
    return null;
  }
}

export default async function ProductPage(props: { params: Promise<{ slug: string }> }) {
  const params = await props.params;
  const product = await getProduct(params.slug);
  
  if (!product) notFound();

  return (
    <main className="max-w-5xl mx-auto p-8 text-brand-neutral bg-brand-surface min-h-screen font-mono">
      <header className="mb-8 border-b border-brand-border pb-6">
        <Link href="/" className="text-sm hover:underline mb-4 inline-block font-medium">&lt; Back to Catalogue</Link>
        <div className="flex flex-col md:flex-row gap-8 items-start">
          {product.image_url ? (
            <img 
              src={product.image_url} 
              alt={product.canonical_name} 
              className="w-full md:w-1/3 object-cover border border-brand-border bg-white"
            />
          ) : (
            <div className="w-full md:w-1/3 aspect-square border border-brand-border bg-brand-neutral/5 flex items-center justify-center">
              <span className="text-brand-neutral/30 uppercase tracking-widest text-sm font-bold">No Image</span>
            </div>
          )}
          
          <div className="flex-1 w-full">
            <div className="flex justify-between items-start">
              <div>
                <h1 className="text-3xl font-bold tracking-tight mb-2 uppercase">{product.canonical_name}</h1>
                <h2 className="text-xl text-brand-neutral/80 uppercase tracking-widest mb-4">{product.brand_name}</h2>
              </div>
              <div className="text-right text-xs text-brand-neutral/60 uppercase">
                <div>Market: <span className="font-bold">{product.market_code}</span></div>
                {product.gtin && <div>GTIN: {product.gtin}</div>}
              </div>
            </div>

            <div className="flex flex-col gap-4">
              <div className="flex flex-wrap gap-4 text-sm uppercase bg-white border border-brand-border p-3 font-bold">
                <span className="text-brand-neutral">Overall: {product.rating_band || "UNRATED"}</span>
                <span className="border-l border-brand-border pl-4">{product.rating_total !== null ? `${product.rating_total}/100` : "N/A"}</span>
                <span className="border-l border-brand-border pl-4 text-brand-neutral/60">Confidence: {product.confidence_grade}</span>
              </div>
              
              {product.component_scores && (
                <div className="flex flex-wrap gap-4 text-xs uppercase bg-brand-neutral/5 border border-brand-border p-2">
                  <span>Nutrition: {product.component_scores.nutrition_score !== null ? product.component_scores.nutrition_score : "N/A"}</span>
                  <span className="border-l border-brand-border pl-4">Ingredient: {product.component_scores.ingredient_score !== null ? product.component_scores.ingredient_score : "N/A"}</span>
                  <span className="border-l border-brand-border pl-4">Context: {product.component_scores.context_score !== null ? product.component_scores.context_score : "N/A"}</span>
                </div>
              )}
            </div>

            {product.flags && product.flags.length > 0 && (
              <div className="mt-4 flex flex-wrap gap-2">
                {product.flags.map((flag, idx) => (
                  <span key={idx} className="text-xs uppercase font-bold border border-red-800 bg-red-100 text-red-900 px-2 py-1">
                    {flag.label}
                  </span>
                ))}
              </div>
            )}
            
            {product.explanation?.summary && (
              <p className="mt-6 text-sm leading-relaxed border border-brand-border p-4 bg-white">
                {product.explanation.summary}
              </p>
            )}

            <div className="mt-4 flex justify-between items-center text-xs uppercase text-brand-neutral/50">
              {product.methodology_version && <span>Method: {product.methodology_version}</span>}
              {product.last_reviewed_at && <span>Reviewed: {new Date(product.last_reviewed_at).toLocaleDateString()}</span>}
            </div>
          </div>
        </div>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <section className="space-y-6">
          <h2 className="text-xl font-semibold border-b border-brand-border pb-2 uppercase tracking-tight">Ingredients</h2>
          {product.ingredients.length === 0 ? (
            <p className="text-sm border border-brand-border p-4 bg-white">No ingredient data available.</p>
          ) : (
            <div className="border border-brand-border bg-white p-5">
              <ul className="space-y-3">
                {product.ingredients.map((ing, idx) => (
                  <li key={idx} className="flex justify-between items-center text-sm border-b border-brand-border border-dashed pb-2 last:border-0 last:pb-0">
                    <span className="uppercase flex-1">{ing.label_text}</span>
                    <span className="text-xs uppercase text-brand-neutral/40 ml-4 flex-shrink-0 font-mono">
                      {String(ing.position).padStart(2, '0')}
                    </span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </section>

        <section className="space-y-6">
          <h2 className="text-xl font-semibold border-b border-brand-border pb-2 uppercase tracking-tight">Nutrition (per 100g)</h2>
          {!product.nutrition ? (
            <p className="text-sm border border-brand-border p-4 bg-white">No nutrition facts logged.</p>
          ) : (
            <div className="border border-brand-border bg-white p-5 text-sm uppercase space-y-3">
              <div className="flex justify-between border-b border-brand-border pb-2 font-bold">
                <span>Energy (kcal)</span>
                <span>{product.nutrition.energy !== null ? product.nutrition.energy : "N/A"}</span>
              </div>
              <div className="flex justify-between border-b border-brand-border border-dashed pb-2">
                <span>Fat</span>
                <span>{product.nutrition.fat !== null ? `${product.nutrition.fat}g` : "N/A"}</span>
              </div>
              <div className="flex justify-between border-b border-brand-border border-dashed pb-2 ml-4">
                <span className="text-brand-neutral/70">Saturated Fat</span>
                <span>{product.nutrition.saturated_fat !== null ? `${product.nutrition.saturated_fat}g` : "N/A"}</span>
              </div>
              <div className="flex justify-between border-b border-brand-border border-dashed pb-2">
                <span>Sugars</span>
                <span>{product.nutrition.sugars !== null ? `${product.nutrition.sugars}g` : "N/A"}</span>
              </div>
              <div className="flex justify-between border-b border-brand-border border-dashed pb-2">
                <span>Sodium</span>
                <span>{product.nutrition.sodium !== null ? `${product.nutrition.sodium}g` : "N/A"}</span>
              </div>
            </div>
          )}
        </section>
      </div>
    </main>
  );
}
