"use client";

import { useState } from "react";
import Link from "next/link";

export default function ReportPage() {
  const [status, setStatus] = useState<"idle" | "submitting" | "success" | "error">("idle");
  const [reference, setReference] = useState<string | null>(null);

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setStatus("submitting");

    const formData = new FormData(e.currentTarget);
    const payload = {
      reporter_contact: formData.get("reporter_contact") as string,
      entity_type: formData.get("entity_type") as string,
      entity_id: formData.get("entity_id") as string,
      message: formData.get("message") as string,
    };

    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/v1/corrections`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!res.ok) throw new Error("Submission failed");
      
      const data = await res.json();
      setReference(data.reference_number);
      setStatus("success");
    } catch (err) {
      setStatus("error");
    }
  }

  return (
    <main className="max-w-3xl mx-auto p-8 text-brand-neutral bg-brand-surface min-h-screen">
      <header className="mb-8 border-b border-brand-border pb-6">
        <Link href="/" className="text-sm hover:underline mb-4 inline-block font-medium">&lt; Back to Home</Link>
        <h1 className="text-3xl font-bold tracking-tight">Submit a Correction</h1>
        <p className="text-sm mt-1">Request a product update, missing item, or report an inaccuracy.</p>
      </header>

      {status === "success" ? (
        <div className="border border-brand-neutral p-6 bg-white text-center">
          <h2 className="text-xl font-bold mb-2">Correction Submitted</h2>
          <p className="text-sm mb-4">Thank you. Your request has been logged for editorial review.</p>
          <div className="inline-block border border-brand-border bg-brand-surface px-4 py-2 font-mono text-lg font-bold">
            {reference}
          </div>
          <p className="text-xs text-gray-600 mt-4">Please save this reference number for your records.</p>
        </div>
      ) : (
        <form onSubmit={handleSubmit} className="border border-brand-border bg-white p-6 space-y-6">
          {status === "error" && (
            <div className="bg-red-50 border border-red-200 text-red-800 px-4 py-3 text-sm">
              An error occurred while submitting your request. Please try again.
            </div>
          )}
          
          <div className="space-y-2">
            <label htmlFor="entity_type" className="block text-sm font-semibold">Issue Type</label>
            <select id="entity_type" name="entity_type" required className="w-full border border-brand-border p-2 focus:outline-none focus:ring-1 focus:ring-brand-neutral bg-white text-sm">
              <option value="product">Product Inaccuracy</option>
              <option value="ingredient">Ingredient Information</option>
              <option value="missing_product">Missing Product</option>
              <option value="other">Other</option>
            </select>
          </div>

          <div className="space-y-2">
            <label htmlFor="entity_id" className="block text-sm font-semibold">Related ID or URL</label>
            <input type="text" id="entity_id" name="entity_id" required placeholder="e.g., product slug or UUID" className="w-full border border-brand-border p-2 focus:outline-none focus:ring-1 focus:ring-brand-neutral text-sm" />
          </div>

          <div className="space-y-2">
            <label htmlFor="message" className="block text-sm font-semibold">Details and Evidence</label>
            <textarea id="message" name="message" required rows={5} placeholder="Provide details and links to evidence supporting this correction..." className="w-full border border-brand-border p-2 focus:outline-none focus:ring-1 focus:ring-brand-neutral text-sm"></textarea>
          </div>

          <div className="space-y-2">
            <label htmlFor="reporter_contact" className="block text-sm font-semibold">Email Address (Optional)</label>
            <input type="email" id="reporter_contact" name="reporter_contact" placeholder="For follow-up questions" className="w-full border border-brand-border p-2 focus:outline-none focus:ring-1 focus:ring-brand-neutral text-sm" />
          </div>

          <button 
            type="submit" 
            disabled={status === "submitting"}
            className="w-full bg-brand-neutral text-brand-surface px-6 py-3 font-semibold hover:opacity-90 disabled:opacity-50 transition-opacity"
          >
            {status === "submitting" ? "Submitting..." : "Submit Correction Request"}
          </button>
        </form>
      )}
    </main>
  );
}
