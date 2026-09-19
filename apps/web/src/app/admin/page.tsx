export default function AdminDashboardPage() {
  return (
    <div className="max-w-6xl">
      <h1 className="text-3xl font-bold tracking-tight mb-8 pb-4 border-b border-brand-border">Admin Dashboard</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div className="border border-brand-border bg-white p-6">
          <h2 className="text-sm font-semibold text-gray-700 uppercase mb-2 font-mono">Pending Reviews</h2>
          <p className="text-4xl font-bold font-mono">14</p>
        </div>
        <div className="border border-brand-border bg-white p-6">
          <h2 className="text-sm font-semibold text-gray-700 uppercase mb-2 font-mono">Open Corrections</h2>
          <p className="text-4xl font-bold font-mono">3</p>
        </div>
        <div className="border border-brand-border bg-white p-6">
          <h2 className="text-sm font-semibold text-gray-700 uppercase mb-2 font-mono">Total Products</h2>
          <p className="text-4xl font-bold font-mono">2,109</p>
        </div>
        <div className="border border-brand-border bg-white p-6">
          <h2 className="text-sm font-semibold text-gray-700 uppercase mb-2 font-mono">Outbox Queue</h2>
          <p className="text-4xl font-bold font-mono">0</p>
        </div>
      </div>

      <div className="border border-brand-border bg-white p-6">
        <h2 className="text-xl font-bold mb-4 border-b border-brand-border pb-2">Recent System Activity</h2>
        <ul className="space-y-3 text-sm font-mono text-gray-800">
          <li className="flex justify-between border-b border-brand-surface pb-2">
            <span>[SYS] Processed indexing for 14 variants</span>
            <span className="text-gray-500">10 mins ago</span>
          </li>
          <li className="flex justify-between border-b border-brand-surface pb-2">
            <span>[PUB] Admin published product [SLUG-190]</span>
            <span className="text-gray-500">45 mins ago</span>
          </li>
          <li className="flex justify-between border-b border-brand-surface pb-2">
            <span>[ERR] Webhook failure on external API</span>
            <span className="text-gray-500">2 hours ago</span>
          </li>
          <li className="flex justify-between">
            <span>[PUB] Admin published product [SLUG-189]</span>
            <span className="text-gray-500">5 hours ago</span>
          </li>
        </ul>
      </div>
    </div>
  );
}
