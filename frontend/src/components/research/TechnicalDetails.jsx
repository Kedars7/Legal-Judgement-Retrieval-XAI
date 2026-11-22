import { useId, useState } from "react";
import { ChevronDown } from "lucide-react";
import ExplanationPanel from "./ExplanationPanel.jsx";
import { cn } from "../../lib/utils.js";

const humanize = (k) => k.replace(/_/g, " ").replace(/^./, (c) => c.toUpperCase());

const Row = ({ label, value }) => (
  <div className="flex justify-between gap-4 border-b border-black/10 py-2 text-sm last:border-0">
    <dt className="text-muted">{label}</dt><dd className="font-medium tabular-nums">{value}</dd>
  </div>
);

/** Collapsed by default; contents mount only once opened. */
export default function TechnicalDetails({ result }) {
  const [open, setOpen] = useState(false);
  const id = useId();
  const { retrieval: r, explanation } = result;
  return (
    <div className="mt-4">
      <button onClick={() => setOpen((o) => !o)} aria-expanded={open} aria-controls={id}
        className="flex items-center gap-1 rounded text-sm font-medium text-legal-blue hover:underline">
        Technical details <ChevronDown size={16} className={cn("transition-transform", open && "rotate-180")} aria-hidden="true" />
      </button>
      {open && (
        <div id={id} className="mt-3 rounded border border-black/10 bg-legal-paper p-4">
          <dl>
            <Row label="Dense similarity" value={r.dense_score.toFixed(4)} />
            <Row label="BM25 score" value={r.bm25_score.toFixed(2)} />
            <Row label="RRF score" value={r.rrf_score.toFixed(4)} />
            <Row label="Dense rank" value={`#${r.dense_rank}`} />
            <Row label="BM25 rank" value={`#${r.bm25_rank}`} />
            <Row label="Final rank" value={`#${result.rank}`} />
          </dl>
          {Object.keys(explanation.feature_values ?? {}).length > 0 && (
            <>
              <h4 className="mt-6 text-sm font-semibold uppercase tracking-wider text-muted">Model input features</h4>
              <dl>{Object.entries(explanation.feature_values).map(([k, v]) => <Row key={k} label={humanize(k)} value={Number.isInteger(v) ? v : Number(v).toFixed(4)} />)}</dl>
            </>
          )}
          <div className="mt-6"><ExplanationPanel explanation={explanation} /></div>
        </div>
      )}
    </div>
  );
}
