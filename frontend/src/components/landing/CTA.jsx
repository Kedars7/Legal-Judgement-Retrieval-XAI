import { ArrowRight } from "lucide-react";
import PageContainer from "../layout/PageContainer.jsx";
import Button from "../ui/Button.jsx";
import { DISCLAIMER } from "../../lib/utils.js";

export default function CTA() {
  return (
    <PageContainer as="section" className="py-24 md:py-32">
      <div className="rounded-lg bg-legal-blue-tint px-6 py-16 text-center md:px-16 md:py-24">
        <h2 className="h-section mx-auto max-w-3xl">Ready to explore the judgments?</h2>
        <p className="mx-auto mt-6 max-w-2xl text-lg text-muted md:text-xl">Run a legal query and see how hybrid retrieval and explainable AI surface relevant evidence.</p>
        <Button to="/research" size="lg" className="mt-10">Start researching <ArrowRight size={20} aria-hidden="true" /></Button>
        <p className="mt-8 text-sm text-muted">{DISCLAIMER}</p>
      </div>
    </PageContainer>
  );
}
