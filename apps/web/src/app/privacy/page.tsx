export default function PrivacyPolicy() {
  return (
    <main className="max-w-3xl mx-auto p-8 text-foreground">
      <h1 className="text-2xl font-bold mb-4">Privacy Policy</h1>
      <p className="mb-4 text-sm">Last updated: {new Date().toLocaleDateString()}</p>
      <section className="space-y-4 text-sm">
        <p>Gud Fud does not require a public account to browse the catalogue.</p>
        <p>We collect only necessary correction-form data to investigate reports and communicate resolutions. This data is retained only as long as required to resolve the inquiry.</p>
        <p>We do not create health-interest profiles or sell your search analytics.</p>
      </section>
    </main>
  );
}
