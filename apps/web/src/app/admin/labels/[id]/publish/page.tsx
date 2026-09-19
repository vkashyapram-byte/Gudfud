"use client";

import { useState } from "react";

export default function PublishLabelPage({ params }: { params: { id: string } }) {
  const [status, setStatus] = useState<"idle" | "submitting" | "success" | "error">("idle");
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setStatus("submitting");
    setErrorMsg(null);

    const formData = new FormData(e.currentTarget);
    
    // Parse structured JSON explicitly as a string
    let explanationStr = formData.get("explanation") as string;
    if (!explanationStr) {
        explanationStr = "{}";
    }

    const payload = {
      actor_id: formData.get("actor_id") as string,
      methodology_version_id: formData.get("methodology_version_id") as string,
      total_score: parseFloat(formData.get("total_score") as string),
      band: formData.get("band") as string,
      nutrition_score: parseFloat(formData.get("nutrition_score") as string),
      ingredient_score: parseFloat(formData.get("ingredient_score") as string),
      context_score: parseFloat(formData.get("context_score") as string),
      confidence_grade: formData.get("confidence_grade") as string,
      explanation: explanationStr,
    };

    try {
      const res = await fetch(`http://127.0.0.1:8000/v1/admin/labels/${params.id}/publish`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        const errorData = await res.json().catch(() => null);
        throw new Error(errorData?.detail || `HTTP ${res.status} Transaction Failed`);
      }
      
      setStatus("success");
    } catch (err: any) {
      setErrorMsg(err.message || "Unknown transaction error");
      setStatus("error");
    }
  }

  if (status === "success") {
    return (
      <div className="max-w-3xl">
        <div className="border-4 border-brand-neutral p-8 bg-white text-center">
          <h2 className="text-2xl font-bold mb-4 uppercase">Publication Successful</h2>
          <p className="font-mono mb-6">Label Version {params.id} has been atomically published.</p>
          <button onClick={() => setStatus("idle")} className="border-2 border-brand-neutral px-6 py-2 font-bold uppercase hover:bg-brand-surface">
            Publish Another Update
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-3xl">
      <h1 className="text-3xl font-bold tracking-tight mb-8 pb-4 border-b border-brand-border">
        Publish Label Transaction
      </h1>
      <p className="text-sm font-mono mb-6 bg-brand-surface p-3 border border-brand-border">
        Target: <span className="font-bold">{params.id}</span>
      </p>

      {status === "error" && (
        <div className="border border-brand-neutral bg-white p-4 mb-6">
          <h2 className="font-bold font-mono text-lg uppercase mb-1">Transaction Failed</h2>
          <p className="font-mono text-sm">{errorMsg}</p>
        </div>
      )}

      <form onSubmit={handleSubmit} className="border border-brand-border bg-white p-6 space-y-6 text-sm">
        <div className="grid grid-cols-2 gap-6">
          <div className="space-y-2">
            <label htmlFor="actor_id" className="block font-bold">Actor ID (System Identity)</label>
            <input type="text" id="actor_id" name="actor_id" required className="w-full border border-brand-border p-2 focus:outline-none focus:ring-1 focus:ring-brand-neutral bg-white font-mono" />
          </div>
          <div className="space-y-2">
            <label htmlFor="methodology_version_id" className="block font-bold">Methodology UUID</label>
            <input type="text" id="methodology_version_id" name="methodology_version_id" required className="w-full border border-brand-border p-2 focus:outline-none focus:ring-1 focus:ring-brand-neutral bg-white font-mono" />
          </div>
        </div>

        <div className="grid grid-cols-4 gap-6">
          <div className="space-y-2">
            <label htmlFor="total_score" className="block font-bold">Total Score</label>
            <input type="number" step="0.1" id="total_score" name="total_score" required className="w-full border border-brand-border p-2 focus:outline-none focus:ring-1 focus:ring-brand-neutral bg-white font-mono" />
          </div>
          <div className="space-y-2">
            <label htmlFor="nutrition_score" className="block font-bold">Nutrition (0-60)</label>
            <input type="number" step="0.1" id="nutrition_score" name="nutrition_score" required className="w-full border border-brand-border p-2 focus:outline-none focus:ring-1 focus:ring-brand-neutral bg-white font-mono" />
          </div>
          <div className="space-y-2">
            <label htmlFor="ingredient_score" className="block font-bold">Ingredient (0-25)</label>
            <input type="number" step="0.1" id="ingredient_score" name="ingredient_score" required className="w-full border border-brand-border p-2 focus:outline-none focus:ring-1 focus:ring-brand-neutral bg-white font-mono" />
          </div>
          <div className="space-y-2">
            <label htmlFor="context_score" className="block font-bold">Context (0-15)</label>
            <input type="number" step="0.1" id="context_score" name="context_score" required className="w-full border border-brand-border p-2 focus:outline-none focus:ring-1 focus:ring-brand-neutral bg-white font-mono" />
          </div>
        </div>

        <div className="grid grid-cols-2 gap-6">
          <div className="space-y-2">
            <label htmlFor="band" className="block font-bold">Rating Band</label>
            <input type="text" id="band" name="band" required placeholder="e.g. Needs Improvement" className="w-full border border-brand-border p-2 focus:outline-none focus:ring-1 focus:ring-brand-neutral bg-white font-mono" />
          </div>
          <div className="space-y-2">
            <label htmlFor="confidence_grade" className="block font-bold">Confidence Grade</label>
            <select id="confidence_grade" name="confidence_grade" required className="w-full border border-brand-border p-2 focus:outline-none focus:ring-1 focus:ring-brand-neutral bg-white font-mono">
              <option value="A">A - Exceptional</option>
              <option value="B">B - Adequate</option>
              <option value="C">C - Mediocre</option>
              <option value="D">D - Poor</option>
            </select>
          </div>
        </div>

        <div className="space-y-2">
          <label htmlFor="explanation" className="block font-bold">Explanation (JSON Payload)</label>
          <textarea id="explanation" name="explanation" required rows={4} defaultValue="{}" className="w-full border border-brand-border p-2 focus:outline-none focus:ring-1 focus:ring-brand-neutral bg-white font-mono"></textarea>
        </div>

        <button 
          type="submit" 
          disabled={status === "submitting"}
          className="w-full border-2 border-brand-neutral bg-brand-neutral text-brand-surface px-6 py-4 font-bold uppercase hover:bg-white hover:text-brand-neutral transition-none disabled:opacity-50"
        >
          {status === "submitting" ? "Executing Transaction..." : "Commit Publication"}
        </button>
      </form>
    </div>
  );
}
