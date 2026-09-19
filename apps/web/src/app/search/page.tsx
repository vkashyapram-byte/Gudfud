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
    const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/v1/search?q=${encodeURIComponent(query)}`, { cache: "no-store" });
    if (!res.ok) return null;
    return res.json();
  } catch (error) {
    return null;
  }
}

export default async function SearchPage({ searchParams }: { searchParams: { q?: string } }) {
  const query = searchParams.q || "";
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
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6">
          {results.items.map((item, idx) => (
            <Link 
              key={`${item.type}-${item.slug}-${idx}`} 
              href={item.type === 'brand' ? `/brands/${item.slug}` : `/products/${item.slug}`} 
              className={`block p-4 bg-white hover:bg-brand-surface transition-colors ${
                item.type === 'brand' ? 'border-2 border-brand-neutral' : 'border border-brand-border'
              }`}
            >
              <div className="flex justify-between items-start mb-2">
                <span className="text-xs uppercase font-mono bg-brand-surface border border-brand-border px-1">
                  {item.type}
                </span>
              </div>
              <h3 className="font-bold text-lg leading-tight mb-1">{item.name}</h3>
              {item.subtitle && <p className="text-sm text-gray-700">{item.subtitle}</p>}
            </Link>
          ))}
        </div>
      )}
    </main>
  );
}
