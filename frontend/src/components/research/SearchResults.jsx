import { RotateCw } from "lucide-react";
import Button from "../ui/Button.jsx";
import JudgmentCard from "./JudgmentCard.jsx";
import { DISCLAIMER } from "../../lib/utils.js";

export function ResultsMessage({ title, body, onRetry }) {
  return (
    <div role="alert" className="rounded-lg border border-black/10 bg-legal-white p-8 text-center md:p-12">
      <h2 className="text-2xl font-semibold">{title}</h2>
      {body && <p className="mx-auto mt-3 max-w-md text-muted">{body}</p>}
      {onRetry && <Button onClick={onRetry} className="mt-6"><RotateCw size={16} aria-hidden="true" />Try again</Button>}
    </div>
  );
}

export default function SearchResults({ data, onViewDetails }) {
  const { results, total_results, retrieval } = data;
  return (
    <section aria-labelledby="results-heading">
      <h2 id="results-heading" role="status" className="text-3xl font-bold tracking-tight">
        {total_results} {total_results === 1 ? "judgment" : "judgments"} found
      </h2>
      <p className="mt-2 text-sm text-muted">
        Hybrid retrieval: top {retrieval.dense_top_k} semantic + top {retrieval.bm25_top_k} lexical candidates, fused with RRF (k={retrieval.rrf_constant}).
      </p>
      <ol className="mt-8 space-y-6">
        {results.map((r, i) => <JudgmentCard key={r.rank} result={r} index={i} onViewDetails={onViewDetails} />)}
      </ol>
      <p className="mt-8 text-sm text-muted">{DISCLAIMER}</p>
    </section>
  );
}
