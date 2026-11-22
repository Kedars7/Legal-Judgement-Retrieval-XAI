import { useEffect, useState } from "react";
import { motion, useReducedMotion } from "framer-motion";
import PageContainer from "../layout/PageContainer.jsx";
import Button from "../ui/Button.jsx";
import { mockSearchResponse } from "../../data/mockSearchResponse.js";
import { formatPercent, padRank } from "../../lib/utils.js";

const QUERY = "Whether the accused is entitled to protection under Article 14...";
const TYPING_MS = 28;

/** Types the query character by character; shows full text immediately under reduced motion. */
function useTyped(text, enabled) {
  const [n, setN] = useState(enabled ? 0 : text.length);
  useEffect(() => {
    if (!enabled) return setN(text.length);
    const t = setInterval(() => setN((v) => (v >= text.length ? (clearInterval(t), v) : v + 1)), TYPING_MS);
    return () => clearInterval(t);
  }, [text, enabled]);
  return text.slice(0, n);
}

function HeroPreview() {
  const reduce = useReducedMotion();
  const typed = useTyped(QUERY, !reduce);
  return (
    <div className="rounded-lg border border-black/10 bg-legal-white p-5 shadow-subtle md:p-8" aria-hidden="true">
      <p className="text-sm font-medium text-muted">Query</p>
      <p className="mt-2 min-h-[56px] text-lg font-medium md:text-xl">
        {typed}<span className="ml-0.5 inline-block h-5 w-0.5 translate-y-1 animate-pulse bg-legal-blue" />
      </p>
      <div className="mt-6 space-y-3">
        {mockSearchResponse.results.map((r, i) => (
          <motion.div key={r.rank} initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }}
            transition={{ delay: reduce ? 0 : 1.2 + i * 0.35, duration: 0.4 }}
            className="rounded border border-black/10 bg-legal-paper p-4">
            <div className="flex items-center justify-between gap-4">
              <p className="truncate text-base font-semibold"><span className="mr-3 text-legal-blue">{padRank(r.rank)}</span>{r.case.title}</p>
              <span className="shrink-0 text-sm font-semibold text-legal-blue">{formatPercent(r.relevance.model_score)}</span>
            </div>
            <div className="mt-3 h-1 rounded-sm bg-black/10">
              <motion.div className="h-1 rounded-sm bg-legal-blue" initial={{ width: 0 }} animate={{ width: formatPercent(r.relevance.model_score, 0) }}
                transition={{ delay: reduce ? 0 : 1.5 + i * 0.35, duration: 0.6 }} />
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  );
}

export default function Hero() {
  return (
    <PageContainer as="section" className="grid items-center gap-16 pb-24 pt-16 md:pt-24 lg:grid-cols-2">
      <div>
        <p className="mb-6 text-sm font-semibold uppercase tracking-wider text-legal-blue">Indian Supreme Court judgments</p>
        <h1 className="h-hero">Search Indian Supreme Court judgments with AI.</h1>
        <p className="mt-8 max-w-xl text-lg text-muted md:text-xl">
          Retrieve legally relevant judgments using semantic search, lexical matching, hybrid ranking, and explainable AI.
        </p>
        <div className="mt-10 flex flex-wrap gap-4">
          <Button to="/research" size="lg">Start researching</Button>
          <Button to="/how-it-works" variant="secondary" size="lg">How it works</Button>
        </div>
      </div>
      <HeroPreview />
    </PageContainer>
  );
}
