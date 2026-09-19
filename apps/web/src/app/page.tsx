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
  last_reviewed_at: string | null;
}

interface PaginatedCatalogue {
  items: ProductCard[];
  total: number;
  page: number;
  size: number;
}

async function fetchRecentProducts(): Promise<ProductCard[]> {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";
  try {
    const res = await fetch(`${apiUrl}/v1/catalogue?page=1&size=12`, {
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
      <header className="border-b border-brand-border p-6 flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
        <div>
          <h1 className="text-3xl font-bold uppercase tracking-tighter">Gud Fud</h1>
          <p className="text-sm mt-1 uppercase tracking-widest text-brand-neutral/70">
            Transparent Food Label Analysis
          </p>
        </div>
        <form action={search} className="w-full md:w-96 flex border border-brand-border">
          <input
            type="text"
            name="q"
            placeholder="SEARCH PRODUCTS, BRANDS, E-NUMBERS..."
            required
            minLength={2}
            className="w-full bg-brand-surface p-3 text-sm outline-none placeholder:text-brand-neutral/40 rounded-none uppercase"
          />
          <button
            type="submit"
            className="border-l border-brand-border px-6 uppercase font-bold hover:bg-brand-neutral hover:text-brand-surface transition-none rounded-none text-sm"
          >
            Search
          </button>
        </form>
      </header>

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
