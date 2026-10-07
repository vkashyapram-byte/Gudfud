import Link from "next/link";

interface IngredientItem {
  slug: string;
  canonical_name: string;
  INS_number: string | null;
  E_number: string | null;
  ingredient_type: string | null;
  technical_function: string | null;
  public_summary: string | null;
  is_generally_safe: boolean | null;
  image_url?: string | null;
}

interface PaginatedIngredients {
  items: IngredientItem[];
  total: number;
  page: number;
  size: number;
}

async function getIngredients(page: number): Promise<PaginatedIngredients> {
  try {
    const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/v1/ingredients?page=${page}&size=24`, {
      next: { revalidate: 300 },
    });
    if (!res.ok) return { items: [], total: 0, page: 1, size: 24 };
    return res.json();
  } catch (error) {
    return { items: [], total: 0, page: 1, size: 24 };
  }
}

export default async function IngredientsCataloguePage({ searchParams }: { searchParams: Promise<{ page?: string }> }) {
  const params = await searchParams;
  const currentPage = parseInt(params.page || "1", 10);
  const catalogue = await getIngredients(currentPage);
  const totalPages = Math.ceil(catalogue.total / catalogue.size) || 1;

  return (
    <main className="max-w-6xl mx-auto p-8 text-brand-neutral bg-brand-surface min-h-screen">
      <header className="mb-8 border-b border-brand-border pb-6 flex justify-between items-baseline">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Ingredients Catalogue</h1>
          <p className="text-sm mt-1">Browse all analyzed ingredients and additives.</p>
        </div>
        <Link href="/catalogue" className="text-sm hover:underline font-medium">&lt; Back to Selection</Link>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-6 mb-12">
        {catalogue.items.map((ingredient) => (
          <Link 
            href={`/ingredients/${ingredient.slug}`} 
            key={ingredient.slug} 
            className="flex flex-col border border-brand-border bg-white hover:border-brand-neutral transition-colors overflow-hidden group"
          >
            <div className="w-full h-40 bg-gray-100 flex items-center justify-center border-b border-brand-border relative overflow-hidden group-hover:opacity-90">
              {ingredient.image_url ? (
                // eslint-disable-next-line @next/next/no-img-element
                <img 
                  src={ingredient.image_url} 
                  alt={ingredient.canonical_name} 
                  className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300" 
                />
              ) : (
                <span className="text-gray-400 text-xs uppercase font-mono">No Image</span>
              )}
            </div>

            <div className="p-5 flex flex-col flex-grow">
              <div className="flex justify-between items-start mb-4">
                <h3 className="font-bold text-lg leading-tight pr-2 group-hover:text-brand-neutral">{ingredient.canonical_name}</h3>
                {(ingredient.E_number || ingredient.INS_number) && (
                  <span className="text-xs border border-brand-border px-1.5 py-0.5 font-mono uppercase shrink-0 text-brand-neutral">
                    {ingredient.E_number || ingredient.INS_number}
                  </span>
                )}
              </div>
            <div className="mb-4 text-sm opacity-80 line-clamp-3 text-gray-700">
              {ingredient.public_summary || "No summary available for this ingredient."}
            </div>

            <div className="mt-auto border-t border-brand-border/20 pt-3 text-xs flex justify-between items-center text-gray-800">
              <span className="font-mono uppercase">{ingredient.ingredient_type || "Unknown Type"}</span>
              {ingredient.is_generally_safe !== null && (
                <span className={`px-2 py-1 ${ingredient.is_generally_safe ? "bg-green-100 text-green-800" : "bg-red-100 text-red-800"}`}>
                  {ingredient.is_generally_safe ? "GRAS" : "Restricted"}
                </span>
              )}
            </div>
            </div>
          </Link>
        ))}
      </div>

      {catalogue.items.length > 0 && (
        <div className="flex justify-between items-center border-t border-brand-border pt-6 text-sm">
          <Link 
            href={`/catalogue/ingredients?page=${Math.max(1, currentPage - 1)}`}
            className={`border border-brand-border px-4 py-2 bg-white hover:bg-brand-surface ${currentPage === 1 ? 'opacity-50 pointer-events-none' : ''}`}
          >
            &lt; Previous
          </Link>
          <span className="font-mono">Page {currentPage} of {totalPages}</span>
          <Link 
            href={`/catalogue/ingredients?page=${Math.min(totalPages, currentPage + 1)}`}
            className={`border border-brand-border px-4 py-2 bg-white hover:bg-brand-surface ${currentPage === totalPages ? 'opacity-50 pointer-events-none' : ''}`}
          >
            Next &gt;
          </Link>
        </div>
      )}

      {catalogue.items.length === 0 && (
        <div className="p-8 border border-brand-border text-center text-sm bg-white">
          No ingredients found in the catalogue.
        </div>
      )}
    </main>
  );
}
