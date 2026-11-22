import PageContainer from "../components/layout/PageContainer.jsx";
import SectionHeading from "../components/ui/SectionHeading.jsx";
import Button from "../components/ui/Button.jsx";
import Pipeline from "../components/architecture/Pipeline.jsx";
import ArchitectureDiagram from "../components/architecture/ArchitectureDiagram.jsx";
import { IMPLEMENTATION_DETAILS, EXPLANATION_NOTE } from "../data/pipeline.js";

export default function HowItWorks() {
  return (
    <>
      <PageContainer as="section" className="pb-16 pt-16 md:pt-24">
        <h1 className="h-hero max-w-4xl">How Legal Research AI works</h1>
        <p className="mt-6 max-w-2xl text-lg text-muted md:text-xl">From a natural-language question to ranked, explainable legal evidence.</p>
      </PageContainer>

      <PageContainer as="section" className="pb-24" aria-label="Interactive pipeline"><Pipeline /></PageContainer>

      <section className="border-y border-black/10 bg-legal-white py-24 md:py-32">
        <PageContainer>
          <SectionHeading title="Technical architecture" description="A React client calls a FastAPI service, which orchestrates the retrieval, scoring and explanation components." />
          <div className="mt-16"><ArchitectureDiagram /></div>
        </PageContainer>
      </section>

      <PageContainer as="section" className="py-24 md:py-32">
        <SectionHeading title="Implementation details" description={EXPLANATION_NOTE} />
        <dl className="mt-12 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {IMPLEMENTATION_DETAILS.map(([k, v]) => (
            <div key={k} className="rounded-lg border border-black/10 bg-legal-white p-6">
              <dt className="text-sm font-semibold uppercase tracking-wider text-legal-blue">{k}</dt>
              <dd className="mt-2 text-lg font-medium">{v}</dd>
            </div>
          ))}
        </dl>
        <Button to="/research" size="lg" className="mt-12">Try the research tool</Button>
      </PageContainer>
    </>
  );
}
