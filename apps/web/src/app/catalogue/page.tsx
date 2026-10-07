import Link from "next/link";

export default function CatalogueSelectionPage() {
  return (
    <main className="max-w-4xl mx-auto p-8 text-brand-neutral bg-brand-surface min-h-screen flex flex-col items-center justify-center">
      <div className="text-center mb-12">
        <h1 className="text-4xl font-bold tracking-tight mb-4">Explore the Database</h1>
        <p className="text-lg">What would you like to explore today?</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8 w-full max-w-2xl">
        <Link 
          href="/catalogue/products"
          className="flex flex-col items-center p-12 bg-white border border-brand-border hover:bg-brand-neutral hover:text-white transition-colors group"
        >
          <svg xmlns="http://www.w3.org/2000/svg" className="h-16 w-16 mb-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" />
          </svg>
          <h2 className="text-2xl font-bold uppercase tracking-widest mb-2">Packaged Food</h2>
          <p className="text-sm opacity-70 text-center">Browse fully analyzed food products and their scores.</p>
        </Link>

        <Link 
          href="/catalogue/ingredients"
          className="flex flex-col items-center p-12 bg-white border border-brand-border hover:bg-brand-neutral hover:text-white transition-colors group"
        >
          <svg xmlns="http://www.w3.org/2000/svg" className="h-16 w-16 mb-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
          </svg>
          <h2 className="text-2xl font-bold uppercase tracking-widest mb-2">Ingredients</h2>
          <p className="text-sm opacity-70 text-center">Explore the raw data on food additives and individual ingredients.</p>
        </Link>
      </div>
      
      <div className="mt-12">
        <Link href="/" className="text-sm font-bold uppercase border border-brand-border px-6 py-2 bg-white hover:bg-brand-surface transition-none">
          &lt; Back to Home
        </Link>
      </div>
    </main>
  );
}
