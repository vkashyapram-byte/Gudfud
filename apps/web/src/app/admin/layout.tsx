import Link from "next/link";

export default function AdminLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex min-h-screen bg-brand-surface text-brand-neutral font-sans">
      <aside className="w-64 border-r border-brand-border bg-white flex flex-col">
        <div className="p-6 border-b border-brand-border font-bold text-xl tracking-tight uppercase">
          Gud Fud Admin
        </div>
        <nav className="flex-1 flex flex-col p-4 space-y-2 text-sm font-semibold">
          <Link href="/admin" className="block border border-transparent hover:border-brand-border px-3 py-2 bg-brand-surface hover:bg-white transition-none">
            Dashboard
          </Link>
          <Link href="/admin/reviews" className="block border border-transparent hover:border-brand-border px-3 py-2 bg-brand-surface hover:bg-white transition-none">
            Review Queue
          </Link>
          <Link href="/admin/products" className="block border border-transparent hover:border-brand-border px-3 py-2 bg-brand-surface hover:bg-white transition-none">
            Products
          </Link>
          <Link href="/admin/audit" className="block border border-transparent hover:border-brand-border px-3 py-2 bg-brand-surface hover:bg-white transition-none">
            Audit Logs
          </Link>
        </nav>
        <div className="p-4 border-t border-brand-border text-xs text-gray-600 font-mono">
          System v1.0.0
        </div>
      </aside>
      <main className="flex-1 p-8">
        {children}
      </main>
    </div>
  );
}
