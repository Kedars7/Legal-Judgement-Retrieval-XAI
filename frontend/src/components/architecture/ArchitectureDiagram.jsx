import { motion } from "framer-motion";
import { cn } from "../../lib/utils.js";

const ENGINES = ["InLegalBERT", "FAISS", "BM25", "RRF", "Random Forest", "SHAP"];

function Node({ children, tone = "plain", className }) {
  return (
    <div className={cn("rounded-lg border px-5 py-4 text-center font-semibold",
      tone === "accent" ? "border-legal-blue bg-legal-blue-tint text-legal-blue" : "border-black/10 bg-legal-white", className)}>
      {children}
    </div>
  );
}

/** Connector line draws downward when scrolled into view. */
function Connector() {
  return (
    <div className="flex justify-center" aria-hidden="true">
      <motion.span className="h-10 w-px origin-top bg-legal-blue" initial={{ scaleY: 0 }} whileInView={{ scaleY: 1 }} viewport={{ once: true }} transition={{ duration: 0.5 }} />
    </div>
  );
}

export default function ArchitectureDiagram() {
  return (
    <figure aria-label="System architecture: React frontend, FastAPI, legal search service, retrieval components, judgment evidence">
      <div className="mx-auto max-w-3xl">
        <Node>React Frontend</Node><Connector />
        <Node>FastAPI</Node><Connector />
        <Node tone="accent">Legal Search Service</Node><Connector />
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-6">
          {ENGINES.map((e, i) => (
            <motion.div key={e} initial={{ opacity: 0, y: 10 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ delay: i * 0.06 }}
              className="rounded-lg border border-black/10 bg-legal-white px-3 py-4 text-center text-sm font-semibold">{e}</motion.div>
          ))}
        </div>
        <Connector />
        <Node tone="accent">Judgment Evidence</Node>
      </div>
    </figure>
  );
}
