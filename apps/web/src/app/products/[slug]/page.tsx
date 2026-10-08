import Link from "next/link";
import { notFound } from "next/navigation";
import { getApiUrl } from "@/lib/api";

interface IngredientMapping {
  label_text: string;
  position: number;
  declared_percent: number | null;
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
  color_status?: string | null;
  explanation: { summary?: string; [key: string]: unknown };
  nutrition: NutritionFacts | null;
  ingredients: IngredientMapping[];
  ingredients_raw?: string | null;
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
    const res = await fetch(`${baseUrl}/v1/products/${slug}`, { next: { revalidate: 300 } });
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

  let imageBorderClass = "border border-brand-border";
  if (product.color_status === "GREEN" || (product.rating_total !== null && product.rating_total >= 70)) {
    imageBorderClass = "border-4 border-green-500";
  } else if (product.color_status === "YELLOW" || (product.rating_total !== null && product.rating_total >= 40 && product.rating_total < 70)) {
    imageBorderClass = "border-4 border-yellow-500";
  } else if (product.color_status === "RED" || (product.rating_total !== null && product.rating_total < 40)) {
    imageBorderClass = "border-4 border-red-500";
  }

  return (
    <main className="max-w-5xl mx-auto p-8 text-brand-neutral bg-brand-surface min-h-screen font-mono">
      <header className="mb-8 border-b border-brand-border pb-6">
        <Link href="/" className="text-sm uppercase font-bold border border-brand-border px-4 py-2 hover:bg-brand-neutral hover:text-brand-surface transition-none bg-white mb-4 inline-block">&lt; Back to Catalogue</Link>
        <div className="flex flex-col md:flex-row gap-8 items-start">
          {product.image_url ? (
            <img 
              src={product.image_url.replace(/^http:/, 'https:')} 
              alt={product.canonical_name} 
              className={`w-full md:w-1/3 aspect-square object-cover bg-white ${imageBorderClass}`}
              referrerPolicy="no-referrer"
            />
          ) : (
            <div className={`w-full md:w-1/3 aspect-square bg-brand-neutral/5 flex items-center justify-center ${imageBorderClass}`}>
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
              <div className="flex flex-col sm:flex-row sm:items-center gap-2 sm:gap-0 text-sm uppercase bg-white border border-brand-border p-3 font-bold sm:divide-x sm:divide-brand-border">
                <span className="text-brand-neutral sm:pr-4">Overall: {product.rating_band || "UNRATED"}</span>
                <span className="sm:px-4">{product.rating_total !== null ? `${product.rating_total}/100` : "N/A"}</span>
                <span className="sm:pl-4 text-brand-neutral/60">Confidence: {product.confidence_grade}</span>
              </div>
              
              {product.component_scores && (
                <div className="flex flex-col sm:flex-row sm:items-center gap-1 sm:gap-0 text-xs uppercase bg-brand-neutral/5 border border-brand-border p-2 sm:divide-x sm:divide-brand-border">
                  <span className="sm:pr-4">Nutrition: {product.component_scores.nutrition_score !== null ? product.component_scores.nutrition_score : "N/A"}</span>
                  <span className="sm:px-4">Ingredient: {product.component_scores.ingredient_score !== null ? product.component_scores.ingredient_score : "N/A"}</span>
                  <span className="sm:pl-4">Context: {product.component_scores.context_score !== null ? product.component_scores.context_score : "N/A"}</span>
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
            <p className="text-sm border border-brand-border p-4 bg-white">
              {product.ingredients_raw ? product.ingredients_raw : "No ingredient data available."}
            </p>
          ) : (
            <div className="border border-brand-border bg-white p-5 space-y-4">
              <p className="text-xs text-brand-neutral/70 italic mb-2">
                * Ingredients are listed in descending order by weight as per labeling regulations. Exact percentages are shown where declared by the manufacturer.
              </p>
              <ul className="space-y-3">
                {product.ingredients.map((ing, i) => (
                  <li key={i} className="flex flex-col sm:flex-row sm:items-start justify-between border-b border-brand-border/30 pb-2 last:border-0 last:pb-0 gap-1 sm:gap-4">
                    <span className="text-sm font-medium break-words">{ing.label_text || ing.canonical_name || "Unknown"}</span>
                    <span className="text-xs uppercase text-brand-neutral/40 sm:flex-shrink-0 font-mono sm:text-right">
                      {ing.declared_percent ? `${ing.declared_percent}%` : `Rank #${ing.position}`}
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
              <div className="flex justify-between border-b border-brand-border border-dashed pb-2 ml-4 text-brand-neutral/70">
                <span>Saturated Fat</span>
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
          {product.nutrition && (
            <NutritionAssessment nutrition={product.nutrition} explanation={product.explanation} />
          )}
        </section>
      </div>
    </main>
  );
}

function NutritionAssessment({ nutrition, explanation }: { nutrition: NutritionFacts, explanation: any }) {
  const good: string[] = [];
  const bad: string[] = [];

  if (nutrition.sugars !== null) {
    if (nutrition.sugars > 15) bad.push("High in sugar, which can lead to energy crashes and metabolic issues.");
    else if (nutrition.sugars < 5) good.push("Low sugar content, making it a better choice for blood sugar management.");
  }

  if (nutrition.sodium !== null) {
    if (nutrition.sodium > 1.5) bad.push("High sodium content, which may negatively impact blood pressure.");
    else if (nutrition.sodium < 0.14) good.push("Low sodium, good for heart health.");
  }

  if (nutrition.saturated_fat !== null) {
    if (nutrition.saturated_fat > 5) bad.push("High saturated fat, which should be consumed in moderation.");
    else if (nutrition.saturated_fat < 1.5) good.push("Low saturated fat, which is generally healthier for your heart.");
  }

  if (nutrition.energy !== null) {
    if (nutrition.energy > 400) bad.push("High in calories (energy dense), meaning it's easy to overconsume.");
    else if (nutrition.energy < 40) good.push("Low in calories, which can fit easily into most diets.");
  }

  // Also check explanation for NOVA
  if (Array.isArray(explanation)) {
    const isUltraProcessed = explanation.find((e: any) => e.factor === "nova_4");
    if (isUltraProcessed) {
      bad.push("Ultra-processed (NOVA 4), meaning it contains ingredients rarely used in kitchens and is highly industrially formulated.");
    }
  }

  if (good.length === 0 && bad.length === 0) {
    return (
      <div className="mt-4 p-4 border border-brand-border bg-white text-sm">
        <h3 className="font-bold uppercase mb-2">About the Nutrition</h3>
        <p className="text-brand-neutral/80">This product has moderate nutritional values without extreme highs or lows in sugar, sodium, or saturated fat per 100g.</p>
      </div>
    );
  }

  return (
    <div className="mt-4 p-4 border border-brand-border bg-white text-sm">
      <h3 className="font-bold uppercase mb-4 tracking-tight text-lg">Nutrition Summary</h3>
      <div className="space-y-4">
        {bad.length > 0 && (
          <div>
            <h4 className="font-bold text-red-600 uppercase text-xs mb-2 tracking-widest border-b border-red-200 pb-1 inline-block">The Bad</h4>
            <ul className="list-disc pl-5 space-y-1.5 text-brand-neutral/80 marker:text-red-400">
              {bad.map((text, i) => <li key={i}>{text}</li>)}
            </ul>
          </div>
        )}
        {good.length > 0 && (
          <div>
            <h4 className="font-bold text-green-600 uppercase text-xs mb-2 tracking-widest border-b border-green-200 pb-1 inline-block">The Good</h4>
            <ul className="list-disc pl-5 space-y-1.5 text-brand-neutral/80 marker:text-green-400">
              {good.map((text, i) => <li key={i}>{text}</li>)}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
}
