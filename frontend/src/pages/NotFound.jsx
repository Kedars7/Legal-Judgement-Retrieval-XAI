import PageContainer from "../components/layout/PageContainer.jsx";
import Button from "../components/ui/Button.jsx";

export default function NotFound() {
  return (
    <PageContainer className="py-32">
      <p className="text-sm font-semibold uppercase tracking-wider text-legal-blue">404</p>
      <h1 className="h-hero mt-4">This page could not be found.</h1>
      <p className="mt-6 max-w-xl text-lg text-muted">The page you are looking for does not exist or has moved.</p>
      <Button to="/" size="lg" className="mt-10">Back to home</Button>
    </PageContainer>
  );
}
