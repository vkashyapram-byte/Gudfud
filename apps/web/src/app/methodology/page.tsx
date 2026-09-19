import Link from "next/link";

export default function MethodologyPage() {
  return (
    <main className="max-w-4xl mx-auto p-8 text-brand-neutral bg-brand-surface min-h-screen">
      <header className="mb-8 border-b border-brand-border pb-6 flex justify-between items-baseline">
        <h1 className="text-3xl font-bold tracking-tight">Methodology</h1>
        <Link href="/" className="text-sm hover:underline font-medium">Home</Link>
      </header>

      <section className="mb-12">
        <h2 className="text-2xl font-bold mb-4">Scoring Weights (100-Point Scale)</h2>
        <table className="w-full text-left border-collapse border border-brand-border bg-white text-sm">
          <thead>
            <tr className="bg-brand-surface border-b border-brand-border">
              <th className="p-4 border-r border-brand-border font-bold">Category</th>
              <th className="p-4 border-r border-brand-border font-bold w-24">Points</th>
              <th className="p-4 font-bold">Description</th>
            </tr>
          </thead>
          <tbody>
            <tr className="border-b border-brand-border">
              <td className="p-4 border-r border-brand-border font-semibold">Nutrition</td>
              <td className="p-4 border-r border-brand-border font-mono">60</td>
              <td className="p-4 text-gray-800">Evaluation of macro and micronutrient density, normalized per 100g/ml. Heavily penalizes excessive added sugars, sodium, and saturated fats relative to baseline category guidelines.</td>
            </tr>
            <tr className="border-b border-brand-border">
              <td className="p-4 border-r border-brand-border font-semibold">Ingredient Evidence</td>
              <td className="p-4 border-r border-brand-border font-mono">25</td>
              <td className="p-4 text-gray-800">Assessment of formulation safety and clinical consensus. Penalties apply for additives with high-grade negative clinical evidence or heavily restricted regulatory statuses.</td>
            </tr>
            <tr>
              <td className="p-4 border-r border-brand-border font-semibold">Product Context</td>
              <td className="p-4 border-r border-brand-border font-mono">15</td>
              <td className="p-4 text-gray-800">Review of packaging claims versus ingredient realities, serving size integrity, and overall transparency of the manufacturer.</td>
            </tr>
          </tbody>
        </table>
      </section>

      <section>
        <h2 className="text-2xl font-bold mb-4">Confidence Grades</h2>
        <table className="w-full text-left border-collapse border border-brand-border bg-white text-sm">
          <thead>
            <tr className="bg-brand-surface border-b border-brand-border">
              <th className="p-4 border-r border-brand-border font-bold w-24">Grade</th>
              <th className="p-4 font-bold">Definition</th>
            </tr>
          </thead>
          <tbody>
            <tr className="border-b border-brand-border">
              <td className="p-4 border-r border-brand-border font-mono font-bold text-center text-lg">A</td>
              <td className="p-4 text-gray-800">Exceptional alignment with health guidelines. Negligible controversial additives. Total score 90 - 100.</td>
            </tr>
            <tr className="border-b border-brand-border">
              <td className="p-4 border-r border-brand-border font-mono font-bold text-center text-lg">B</td>
              <td className="p-4 text-gray-800">Adequate nutritional profile. May contain minor, standard preservatives with benign regulatory standing. Total score 75 - 89.</td>
            </tr>
            <tr className="border-b border-brand-border">
              <td className="p-4 border-r border-brand-border font-mono font-bold text-center text-lg">C</td>
              <td className="p-4 text-gray-800">Mediocre profile. High likelihood of excessive sodium/sugar or reliance on heavily processed ingredients. Total score 50 - 74.</td>
            </tr>
            <tr>
              <td className="p-4 border-r border-brand-border font-mono font-bold text-center text-lg">D</td>
              <td className="p-4 text-gray-800">Poor formulation. Substantial inclusion of ingredients with restrictive regulatory contexts or detrimental nutritional values. Total score &lt; 50.</td>
            </tr>
          </tbody>
        </table>
      </section>
    </main>
  );
}
