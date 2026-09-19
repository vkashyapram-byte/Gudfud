import Link from "next/link";

interface ProductCard {
  slug: string;
  canonical_name: string;
  brand: { name: string; slug: string };
  category: { name: string; slug: string };
  rating_band: string | null;
  confidence_grade: string | null;
  market_code: string;
  last_reviewed_at: string | null;
}

interface PaginatedCatalogue {
  items: ProductCard[];
  total: number;
  page: number;
  size: number;
}

async function getCatalogue(page: number): Promise<PaginatedCatalogue> {
  try {
    const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/v1/catalogue?page=${page}&size=24&market=in`, {
      cache: "no-store",
    });
    if (!res.ok) return { items: [], total: 0, page: 1, size: 24 };
    return res.json();
  } catch (error) {
    return { items: [], total: 0, page: 1, size: 24 };
  }
}

export default async function CataloguePage({ searchParams }: { searchParams: { page?: string } }) {
  const currentPage = parseInt(searchParams.page || "1", 10);
  const catalogue = await getCatalogue(currentPage);
  const totalPages = Math.ceil(catalogue.total / catalogue.size) || 1;

  return (
    <main className="max-w-6xl mx-auto p-8 text-brand-neutral bg-brand-surface min-h-screen">
      <header className="mb-8 border-b border-brand-border pb-6 flex justify-between items-baseline">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Catalogue</h1>
          <p className="text-sm mt-1">Browse all published product analyses.</p>
        </div>
        <Link href="/" className="text-sm hover:underline font-medium">Home</Link>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-6 mb-12">
        {catalogue.items.map((product) => (
          <Link 
            href={`/products/${product.slug}`} 
            key={product.slug} 
            className="flex flex-col border border-brand-border p-4 bg-white hover:border-brand-neutral transition-colors"
          >
            <div className="flex justify-between items-start mb-2">
              <h3 className="font-bold text-base leading-tight pr-2">{product.canonical_name}</h3>
              <span className="text-xs bg-brand-surface border border-brand-border px-1.5 py-0.5 font-mono uppercase shrink-0">
                {product.market_code}
              </span>
            </div>
            <p className="text-xs mb-4 text-gray-800">{product.brand.name} | {product.category.name}</p>
            
            <div className="mt-auto border-t border-brand-border pt-3 text-xs">
              <span className="block font-semibold">Rating: {product.rating_band || "Unrated"}</span>
              <span className="block text-gray-600 mt-1">Confidence: {product.confidence_grade || "N/A"}</span>
            </div>
          </Link>
        ))}
      </div>

      {catalogue.items.length > 0 && (
        <div className="flex justify-between items-center border-t border-brand-border pt-6 text-sm">
          <Link 
            href={`/catalogue?page=${Math.max(1, currentPage - 1)}`}
            className={`border border-brand-border px-4 py-2 bg-white hover:bg-brand-surface ${currentPage === 1 ? 'opacity-50 pointer-events-none' : ''}`}
          >
            &lt; Previous
          </Link>
          <span className="font-mono">Page {currentPage} of {totalPages}</span>
          <Link 
            href={`/catalogue?page=${Math.min(totalPages, currentPage + 1)}`}
            className={`border border-brand-border px-4 py-2 bg-white hover:bg-brand-surface ${currentPage === totalPages ? 'opacity-50 pointer-events-none' : ''}`}
          >
            Next &gt;
          </Link>
        </div>
      )}

      {catalogue.items.length === 0 && (
        <div className="p-8 border border-brand-border text-center text-sm bg-white">
          No published products found in the catalogue.
        </div>
      )}
    </main>
  );
}
