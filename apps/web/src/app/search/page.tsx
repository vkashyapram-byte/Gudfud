import Link from "next/link";

interface SearchResultItem {
  type: string;
  name: string;
  slug: string;
  subtitle: string | null;
  similarity_score: number;
}

interface SearchResponse {
  query: string;
  items: SearchResultItem[];
}

async function getSearchResults(query: string): Promise<SearchResponse | null> {
  if (!query || query.length < 2) return null;
  
  try {
    const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/v1/search?q=${encodeURIComponent(query)}&market=in`, { cache: "no-store" });
    if (!res.ok) return null;
    return res.json();
  } catch (error) {
    return null;
  }
}

export default async function SearchPage({ searchParams }: { searchParams: Promise<{ q?: string }> }) {
  const params = await searchParams;
  const query = params.q || "";
  const results = await getSearchResults(query);

  return (
    <main className="max-w-5xl mx-auto p-8 text-brand-neutral bg-brand-surface min-h-screen">
      <header className="mb-8 border-b border-brand-border pb-6 flex justify-between items-baseline">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Search Results</h1>
          <p className="text-sm mt-1">Query: <span className="font-mono bg-white border border-brand-border px-1">{query}</span></p>
        </div>
        <Link href="/" className="text-sm hover:underline font-medium">Home</Link>
      </header>

      {(!results || results.items.length === 0 || query.length < 2) ? (
        <div className="p-8 border border-brand-border text-center text-sm bg-white">
          No results found.
        </div>
      ) : (
        <div className="space-y-12">
          {results.items.filter(item => item.type === 'brand').length > 0 && (
            <section>
              <h2 className="text-xl font-bold uppercase tracking-tight mb-4 border-b border-brand-border pb-2">Brands</h2>
              <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4">
                {results.items.filter(item => item.type === 'brand').map((item, idx) => (
                  <Link 
                    key={`brand-${item.slug}-${idx}`} 
                    href={`/brands/${item.slug}`} 
                    className="block p-4 bg-white hover:bg-brand-surface transition-colors border-2 border-brand-neutral text-center"
                  >
                    <h3 className="font-bold text-lg leading-tight mb-1">{item.name}</h3>
                    {item.subtitle && <p className="text-sm text-gray-700">{item.subtitle}</p>}
                  </Link>
                ))}
              </div>
            </section>
          )}

          {results.items.filter(item => item.type === 'product').length > 0 && (
            <section>
              <h2 className="text-xl font-bold uppercase tracking-tight mb-4 border-b border-brand-border pb-2">Products</h2>
              <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6">
                {results.items.filter(item => item.type === 'product').map((item, idx) => (
                  <Link 
                    key={`product-${item.slug}-${idx}`} 
                    href={`/products/${item.slug}`} 
                    className="block p-4 bg-white hover:bg-brand-surface transition-colors border border-brand-border"
                  >
                    <h3 className="font-bold text-lg leading-tight mb-1">{item.name}</h3>
                    {item.subtitle && <p className="text-sm text-gray-700">{item.subtitle}</p>}
                  </Link>
                ))}
              </div>
            </section>
          )}
        </div>
      )}
    </main>
  );
}
