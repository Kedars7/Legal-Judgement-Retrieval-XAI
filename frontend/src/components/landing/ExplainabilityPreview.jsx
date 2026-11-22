import PageContainer from "../layout/PageContainer.jsx";
import SectionHeading from "../ui/SectionHeading.jsx";
import { FactorList } from "../research/ExplanationPanel.jsx";
import { mockSearchResponse } from "../../data/mockSearchResponse.js";
import { EXPLANATION_NOTE } from "../../data/pipeline.js";

export default function ExplainabilityPreview() {
  const top = mockSearchResponse.results[0];
  const { positive_factors, negative_factors } = top.explanation;
  return (
    <PageContainer as="section" className="py-24 md:py-32">
      <SectionHeading title="Don't just retrieve. Understand why." description={EXPLANATION_NOTE} />
      <div className="mt-16 grid gap-8 rounded-lg border border-black/10 bg-legal-white p-6 md:p-10 lg:grid-cols-2">
        <div>
          <h3 className="text-2xl font-semibold">Why this judgment was retrieved</h3>
          <p className="mt-1 text-muted">{top.case.title}</p>
          <p className="mt-8 text-sm font-semibold uppercase tracking-wider text-legal-blue">Positive contribution</p>
          <FactorList factors={positive_factors} tone="positive" />
          <p className="mt-6 text-sm font-semibold uppercase tracking-wider text-muted">Negative contribution</p>
          <FactorList factors={negative_factors} tone="negative" />
        </div>
        <div className="rounded-lg bg-legal-paper p-6">
          <p className="text-sm font-semibold uppercase tracking-wider text-legal-blue">Evidence</p>
          <p className="mt-4 text-lg leading-relaxed"><span className="rounded-sm bg-legal-teal px-1">{top.evidence}</span></p>
        </div>
      </div>
    </PageContainer>
  );
}
