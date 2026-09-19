import Link from "next/link";

export default function AdminReviewsPage() {
  // Stubbed review data for layout scaffolding
  const reviews = [
    { id: "REV-901", entity: "Brand: Nestle (Update)", requested_by: "System", due_date: "2026-10-01", status: "Pending" },
    { id: "REV-902", entity: "Label: Frito-Lay Classic 2026", requested_by: "User_442", due_date: "2026-10-05", status: "Blocked" },
    { id: "REV-903", entity: "Ingredient: Tartrazine (E102)", requested_by: "Admin_JS", due_date: "2026-10-10", status: "In Progress" },
  ];

  return (
    <div className="max-w-6xl">
      <h1 className="text-3xl font-bold tracking-tight mb-8 pb-4 border-b border-brand-border">Review Queue</h1>
      
      <table className="w-full text-left border-collapse border border-brand-border bg-white text-sm">
        <thead className="bg-brand-surface">
          <tr>
            <th className="p-3 border border-brand-border font-bold uppercase text-xs">Entity</th>
            <th className="p-3 border border-brand-border font-bold uppercase text-xs">Requested By</th>
            <th className="p-3 border border-brand-border font-bold uppercase text-xs">Due Date</th>
            <th className="p-3 border border-brand-border font-bold uppercase text-xs">Status</th>
            <th className="p-3 border border-brand-border font-bold uppercase text-xs w-24">Action</th>
          </tr>
        </thead>
        <tbody>
          {reviews.map((row) => (
            <tr key={row.id}>
              <td className="p-3 border border-brand-border font-semibold">{row.entity}</td>
              <td className="p-3 border border-brand-border font-mono">{row.requested_by}</td>
              <td className="p-3 border border-brand-border font-mono">{row.due_date}</td>
              <td className="p-3 border border-brand-border uppercase text-xs font-bold font-mono tracking-wider">{row.status}</td>
              <td className="p-3 border border-brand-border text-center">
                <Link href={`/admin/reviews/${row.id}`} className="font-bold underline hover:no-underline uppercase text-xs">
                  Review
                </Link>
              </td>
            </tr>
          ))}
          {reviews.length === 0 && (
            <tr>
              <td colSpan={5} className="p-4 border border-brand-border text-center">No pending reviews.</td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
}
