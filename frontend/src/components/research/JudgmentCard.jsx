import { memo, useId, useState } from "react";
import { motion } from "framer-motion";
import { ExternalLink } from "lucide-react";
import Button from "../ui/Button.jsx";
import EvidenceBlock from "./EvidenceBlock.jsx";
import ExplanationPanel from "./ExplanationPanel.jsx";
import TechnicalDetails from "./TechnicalDetails.jsx";
import { formatPercent, padRank } from "../../lib/utils.js";

const TOP_FACTORS = 3;

function JudgmentCard({ result, index, onViewDetails }) {
  const [showExplanation, setShowExplanation] = useState(false);
  const panelId = useId();
  const { case: c, relevance, explanation, evidence } = result;
  const url = c.url; // optional; not part of the current API contract

  return (
    <motion.li initial={{ opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.35, delay: Math.min(index, 6) * 0.07 }}
      className="rounded-lg border border-black/10 bg-legal-white p-6 md:p-8">
      <article aria-label={`Result ${result.rank}: ${c.title}`}>
        <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
          <div>
            <p className="text-sm font-semibold text-legal-blue">{padRank(result.rank)}</p>
            <h3 className="mt-1 text-2xl font-semibold tracking-tight">{c.title}</h3>
            <p className="mt-2 text-muted">{c.date} · {c.citation}</p>
          </div>
          <div className="sm:text-right">
            <p className="text-sm text-muted">Relevance</p>
            <p className="text-3xl font-bold text-legal-blue">{formatPercent(relevance.model_score)}</p>
          </div>
        </div>
        <div className="mt-4 h-1 rounded-sm bg-black/10" role="presentation">
          <div className="h-1 rounded-sm bg-legal-blue" style={{ width: formatPercent(relevance.model_score, 0) }} />
        </div>

        <h4 className="mt-6 text-sm font-semibold uppercase tracking-wider text-muted">Why this result?</h4>
        <ul className="mt-2 flex flex-wrap gap-2">
          {explanation.positive_factors.slice(0, TOP_FACTORS).map((f) => (
            <li key={f.feature} className="rounded-sm bg-legal-blue-tint px-2 py-1 text-sm font-medium text-legal-blue">+ {f.feature}</li>
          ))}
        </ul>

        <EvidenceBlock text={evidence} className="mt-6" />

        <div className="mt-6 flex flex-wrap gap-3">
          <Button variant="secondary" onClick={() => onViewDetails(result)}>View details</Button>
          <Button variant="secondary" onClick={() => setShowExplanation((s) => !s)} aria-expanded={showExplanation} aria-controls={panelId}>
            {showExplanation ? "Hide explanation" : "Show explanation"}
          </Button>
          {url ? (
            <a href={url} target="_blank" rel="noreferrer" className="inline-flex h-10 items-center gap-2 rounded px-4 font-medium text-legal-blue hover:bg-legal-blue-tint">
              Open judgment <ExternalLink size={16} aria-hidden="true" />
            </a>
          ) : (
            <Button variant="ghost" disabled title="The search API did not return a judgment link">Open judgment</Button>
          )}
        </div>

        {showExplanation && (
          <div id={panelId} className="mt-6 rounded-lg border border-black/10 bg-legal-paper p-5">
            <ExplanationPanel explanation={explanation} />
            <TechnicalDetails result={result} />
          </div>
        )}
      </article>
    </motion.li>
  );
}

export default memo(JudgmentCard);
