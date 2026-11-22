import Hero from "../components/landing/Hero.jsx";
import CapabilityGrid from "../components/landing/CapabilityGrid.jsx";
import ProductPreview from "../components/landing/ProductPreview.jsx";
import ExplainabilityPreview from "../components/landing/ExplainabilityPreview.jsx";
import WorkflowPreview from "../components/landing/WorkflowPreview.jsx";
import CTA from "../components/landing/CTA.jsx";

export default function Home() {
  return (
    <>
      <Hero />
      <CapabilityGrid />
      <ProductPreview />
      <ExplainabilityPreview />
      <WorkflowPreview />
      <CTA />
    </>
  );
}
