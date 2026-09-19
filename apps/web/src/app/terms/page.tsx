export default function TermsAndConditions() {
  return (
    <main className="max-w-3xl mx-auto p-8 text-foreground">
      <h1 className="text-2xl font-bold mb-4">Terms and Conditions</h1>
      <p className="mb-4 text-sm">Last updated: {new Date().toLocaleDateString()}</p>
      <section className="space-y-4 text-sm">
        <p>Gud Fud provides general educational information based on product labels and cited sources.</p>
        <p><strong>General Information Only:</strong> The information on this site is not medical advice, does not diagnose or treat any disease, and does not replace consultation with a qualified medical professional.</p>
        <p><strong>Accuracy:</strong> Product formulas and regulations change. Users should always verify the physical package label, particularly for allergies or medical restrictions.</p>
      </section>
    </main>
  );
}
