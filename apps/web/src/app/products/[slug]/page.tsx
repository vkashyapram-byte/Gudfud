import Link from "next/link";
import { notFound } from "next/navigation";

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
}

async function getProduct(slug: string): Promise<ProductAnalysis | null> {
  try {
    const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/v1/products/${slug}`, { cache: "no-store" });
    if (!res.ok) return null;
    return res.json();
  } catch (error) {
    return null;
  }
}

export default async function ProductPage({ params }: { params: { slug: string } }) {
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
          
          <div className="flex-1">
            <h1 className="text-3xl font-bold tracking-tight mb-2 uppercase">{product.canonical_name}</h1>
            <h2 className="text-xl text-brand-neutral/80 uppercase tracking-widest mb-4">{product.brand_name}</h2>
            <div className="flex gap-4 text-sm uppercase bg-white border border-brand-border p-3 inline-flex font-bold">
              <span className="text-brand-neutral">Rating: {product.rating_band || "UNRATED"}</span>
              <span className="border-l border-brand-border pl-4">{product.rating_total ? `${product.rating_total}/100` : "N/A"}</span>
              <span className="border-l border-brand-border pl-4">Market: {product.market_code}</span>
            </div>
            
            {product.explanation?.summary && (
              <p className="mt-6 text-sm leading-relaxed border border-brand-border p-4 bg-white">
                {product.explanation.summary}
              </p>
            )}
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
                    <span className="uppercase">{ing.label_text}</span>
                    {ing.slug ? (
                      <Link href={`/ingredients/${ing.slug}`} className="text-xs uppercase bg-brand-surface border border-brand-border px-2 py-1 hover:bg-brand-neutral hover:text-brand-surface transition-none">
                        Analysis
                      </Link>
                    ) : (
                      <span className="text-xs uppercase text-brand-neutral/40">Unmapped</span>
                    )}
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
