import Link from "next/link";
import { notFound } from "next/navigation";

interface HistoryRecord {
  label_version_id: string;
  version_no: number;
  effective_from: string | null;
  captured_at: string;
  status: string;
  methodology_version: string;
  total_score: number | null;
  rating_band: string | null;
}

interface HistoryResponse {
  history: HistoryRecord[];
}

export default async function ProductHistoryPage(props: { params: Promise<{ slug: string }> }) {
  const params = await props.params;
  const { slug } = params;

  let data: HistoryResponse | null = null;
  try {
    const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/v1/products/${slug}/history`, {
      cache: "no-store",
    });
    if (!res.ok) {
      if (res.status === 404) return notFound();
      throw new Error("Failed to fetch product history");
    }
    data = await res.json();
  } catch (error) {
    console.error(error);
    return (
      <div className="p-8 border border-red-500 bg-red-50 text-red-900">
        <p>Error loading product history.</p>
      </div>
    );
  }

  if (!data || data.history.length === 0) {
    return (
      <div className="p-8 max-w-4xl mx-auto">
        <p className="mb-4 text-brand-neutral">No historical records found for this product.</p>
        <Link href={`/products/${slug}`} className="text-blue-600 underline underline-offset-4 hover:text-blue-800">
          Return to product analysis
        </Link>
      </div>
    );
  }

  return (
    <main className="p-8 max-w-5xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-brand-neutral mb-2">Version History</h1>
        <p className="text-brand-neutral/80">Historical log of all published and archived label records.</p>
        <div className="mt-4">
          <Link href={`/products/${slug}`} className="text-blue-600 underline underline-offset-4 hover:text-blue-800">
            &larr; Back to {slug} analysis
          </Link>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full border-collapse border border-brand-border text-left">
          <thead className="bg-brand-surface border-b border-brand-border">
            <tr>
              <th className="p-4 border-r border-brand-border font-bold">Version</th>
              <th className="p-4 border-r border-brand-border font-bold">Effective Date</th>
              <th className="p-4 border-r border-brand-border font-bold">Status</th>
              <th className="p-4 border-r border-brand-border font-bold">Methodology</th>
              <th className="p-4 font-bold">Score</th>
            </tr>
          </thead>
          <tbody>
            {data.history.map((record) => (
              <tr key={record.label_version_id} className="border-b border-brand-border last:border-0">
                <td className="p-4 border-r border-brand-border font-mono">{record.version_no}</td>
                <td className="p-4 border-r border-brand-border font-mono">
                  {record.effective_from ? new Date(record.effective_from).toISOString().split("T")[0] : "N/A"}
                </td>
                <td className="p-4 border-r border-brand-border uppercase text-sm tracking-wider">
                  {record.status}
                </td>
                <td className="p-4 border-r border-brand-border font-mono">
                  {record.methodology_version}
                </td>
                <td className="p-4">
                  {record.total_score !== null ? (
                    <span className="font-mono">{record.total_score} ({record.rating_band || "N/A"})</span>
                  ) : (
                    <span className="text-brand-neutral/60 font-mono">Pending</span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </main>
  );
}
