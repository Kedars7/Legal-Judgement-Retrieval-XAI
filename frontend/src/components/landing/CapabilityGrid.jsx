import { motion } from "framer-motion";
import { ArrowRight } from "lucide-react";
import { Link } from "react-router-dom";
import PageContainer from "../layout/PageContainer.jsx";
import SectionHeading from "../ui/SectionHeading.jsx";
import CapabilityCard from "./CapabilityCard.jsx";
import { SemanticVisual, HybridVisual, ShapVisual, EvidenceVisual, ReferenceVisual, RankedVisual } from "./CapabilityVisuals.jsx";

const CAPABILITIES = [
  { title: "Semantic Retrieval", description: "Understand the meaning behind a legal query using InLegalBERT embeddings and vector similarity.", visual: <SemanticVisual />, surface: "bg-legal-blue-tint" },
  { title: "Hybrid Search", description: "Combine semantic retrieval with BM25 lexical matching using Reciprocal Rank Fusion.", visual: <HybridVisual />, surface: "bg-legal-teal" },
  { title: "Explainable Retrieval", description: "Understand why a judgment was retrieved through feature-level SHAP explanations.", visual: <ShapVisual />, surface: "bg-legal-paper" },
  { title: "Evidence Grounding", description: "See the exact judgment passage supporting each retrieved result.", visual: <EvidenceVisual />, surface: "bg-legal-paper" },
  { title: "Legal Reference Matching", description: "Identify overlap in Articles, Sections and other legal references.", visual: <ReferenceVisual />, surface: "bg-legal-blue-tint" },
  { title: "Ranked Judgments", description: "Retrieve and organize the most relevant judgments for a research query.", visual: <RankedVisual />, surface: "bg-legal-teal" },
];

export default function CapabilityGrid() {
  return (
    <PageContainer as="section" className="py-24 md:py-32" aria-labelledby="capabilities-heading">
      <SectionHeading
        title="What the system can do"
        action={<Link to="/how-it-works" className="inline-flex items-center gap-2 font-medium text-legal-blue hover:underline">Explore the system <ArrowRight size={18} aria-hidden="true" /></Link>}
      />
      <div className="mt-12 grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {CAPABILITIES.map((c, i) => (
          <motion.div key={c.title} initial={{ opacity: 0, y: 16 }} whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-60px" }} transition={{ duration: 0.4, delay: (i % 3) * 0.08 }}>
            <CapabilityCard {...c} />
          </motion.div>
        ))}
      </div>
    </PageContainer>
  );
}
