import Link from "next/link";
import { redirect } from "next/navigation";

interface ProductCard {
  slug: string;
  canonical_name: string;
  brand: { name: string; slug: string };
  category: { name: string; slug: string };
  rating_band: string | null;
  confidence_grade: string | null;
  market_code: string;
  image_url: string | null;
  last_reviewed_at: string | null;
}

interface PaginatedCatalogue {
  items: ProductCard[];
  total: number;
  page: number;
  size: number;
}

async function fetchRecentProducts(): Promise<ProductCard[]> {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
  try {
    const res = await fetch(`${apiUrl}/v1/catalogue?page=1&size=12&market=in`, {
      cache: "no-store",
    });
    if (!res.ok) return [];
    const data: PaginatedCatalogue = await res.json();
    return data.items;
  } catch (error) {
    return [];
  }
}

export default async function HomePage() {
  const products = await fetchRecentProducts();

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

      <section className="py-20 px-6 flex flex-col items-center justify-center border-b border-brand-border bg-white">
        <div className="w-full max-w-3xl z-10">
          <form action={search} className="flex items-center w-full border border-brand-border bg-white p-2">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-brand-neutral ml-2 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            <input
              type="text"
              name="q"
              placeholder="Search products, brands, e-numbers..."
              required
              minLength={2}
              className="w-full p-3 text-lg outline-none text-brand-neutral placeholder:text-brand-neutral/50 bg-transparent"
            />
          </form>
        </div>
      </section>

      <main className="p-6">
        <div className="mb-6 border-b border-brand-border pb-4 flex justify-between items-end">
          <h2 className="text-xl font-bold uppercase tracking-tight">Recently Reviewed</h2>
          <Link
            href="/catalogue"
            className="text-sm uppercase font-bold border border-brand-border px-4 py-2 hover:bg-brand-neutral hover:text-brand-surface transition-none"
          >
            View Full Catalogue
          </Link>
        </div>

        {products.length === 0 ? (
          <div className="border border-brand-border p-12 text-center">
            <p className="uppercase tracking-widest text-brand-neutral/60">
              No recent reviews available or system is offline.
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {products.map((product) => (
              <Link
                href={`/products/${product.slug}`}
                key={product.slug}
                className="group border border-brand-border p-4 flex flex-col hover:bg-brand-neutral/5 transition-none rounded-none"
              >
                <div className="flex justify-between items-start mb-4">
                  <div className="border border-brand-border px-2 py-1 text-xs uppercase font-bold tracking-wider">
                    {product.rating_band || "UNRATED"}
                  </div>
                  <div className="text-xs uppercase text-brand-neutral/50">
                    {product.market_code}
                  </div>
                </div>
                {product.image_url ? (
                  <div className="w-full h-48 mb-4 border border-brand-border bg-white overflow-hidden">
                    <img src={product.image_url} alt={product.canonical_name} className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300" />
                  </div>
                ) : (
                  <div className="w-full h-48 mb-4 border border-brand-border bg-brand-neutral/5 flex items-center justify-center">
                    <span className="text-brand-neutral/30 uppercase tracking-widest text-xs font-bold">No Image</span>
                  </div>
                )}
                <div className="flex-grow">
                  <h3 className="font-bold text-lg leading-tight uppercase group-hover:underline">
                    {product.canonical_name}
                  </h3>
                  <p className="text-sm mt-1 text-brand-neutral/70 uppercase">
                    {product.brand.name}
                  </p>
                </div>
                <div className="mt-4 pt-4 border-t border-brand-border border-dashed flex justify-between items-center text-xs text-brand-neutral/50">
                  <span className="uppercase">{product.category.name}</span>
                  <span>{product.confidence_grade || "N/A"}</span>
                </div>
              </Link>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
