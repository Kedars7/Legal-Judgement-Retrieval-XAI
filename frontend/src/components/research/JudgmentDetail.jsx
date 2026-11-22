import { useState } from "react";
import Modal from "../ui/Modal.jsx";
import EvidenceBlock from "./EvidenceBlock.jsx";
import ExplanationPanel from "./ExplanationPanel.jsx";
import { formatPercent } from "../../lib/utils.js";
import { cn } from "../../lib/utils.js";

const TABS = ["Overview", "Evidence", "Why retrieved", "Metadata"];

const Field = ({ label, value }) => (
  <div className="border-b border-black/10 py-3">
    <dt className="text-sm text-muted">{label}</dt>
    <dd className="mt-1 font-medium">{value || "—"}</dd>
  </div>
);

function Tabs({ active, onChange }) {
  const onKey = (e) => {
    const i = TABS.indexOf(active);
    if (e.key === "ArrowRight") onChange(TABS[(i + 1) % TABS.length]);
    if (e.key === "ArrowLeft") onChange(TABS[(i - 1 + TABS.length) % TABS.length]);
  };
  return (
    <div role="tablist" aria-label="Judgment details" onKeyDown={onKey} className="-mx-1 flex gap-1 overflow-x-auto border-b border-black/10">
      {TABS.map((t) => (
        <button key={t} role="tab" id={`tab-${t}`} aria-selected={active === t} aria-controls={`panel-${t}`} tabIndex={active === t ? 0 : -1}
          onClick={() => onChange(t)}
          className={cn("whitespace-nowrap border-b-2 px-3 py-3 text-sm font-medium", active === t ? "border-legal-blue text-legal-blue" : "border-transparent text-muted hover:text-legal-ink")}>
          {t}
        </button>
      ))}
    </div>
  );
}

export default function JudgmentDetail({ result, onClose }) {
  const [tab, setTab] = useState(TABS[0]);
  const c = result?.case;
  const r = result?.retrieval;

  return (
    <Modal open={!!result} onClose={onClose} title={c?.title ?? ""}>
      {result && (
        <>
          <Tabs active={tab} onChange={setTab} />
          <div role="tabpanel" id={`panel-${tab}`} aria-labelledby={`tab-${tab}`} className="pt-6">
            {tab === "Overview" && (
              <div>
                <p className="text-sm text-muted">Relevance</p>
                <p className="text-4xl font-bold text-legal-blue">{formatPercent(result.relevance.model_score)}</p>
                <dl className="mt-6">
                  <Field label="Date" value={c.date} />
                  <Field label="Citation" value={c.citation} />
                  <Field label="Final rank" value={`#${result.rank}`} />
                  <Field label="Dense rank / BM25 rank" value={`#${r.dense_rank} / #${r.bm25_rank}`} />
                </dl>
                <EvidenceBlock text={result.evidence} className="mt-6" />
              </div>
            )}
            {tab === "Evidence" && <EvidenceBlock text={result.evidence} label="Relevant passage" collapsible={false} />}
            {tab === "Why retrieved" && (
              <div>
                <dl className="mb-6">
                  <Field label="Dense similarity" value={r.dense_score.toFixed(4)} />
                  <Field label="BM25 score" value={r.bm25_score.toFixed(2)} />
                  <Field label="RRF score" value={r.rrf_score.toFixed(4)} />
                </dl>
                <ExplanationPanel explanation={result.explanation} />
              </div>
            )}
            {tab === "Metadata" && (
              <dl>
                <Field label="Case title" value={c.title} />
                <Field label="Date" value={c.date} />
                <Field label="Citation" value={c.citation} />
                <Field label="Bench" value={c.bench} />
                <Field label="Petitioner" value={c.petitioner} />
                <Field label="Respondent" value={c.respondent} />
              </dl>
            )}
          </div>
        </>
      )}
    </Modal>
  );
}
