import { useCallback, useState } from "react";
import PageContainer from "../components/layout/PageContainer.jsx";
import SearchForm from "../components/research/SearchForm.jsx";
import SearchLoading from "../components/research/SearchLoading.jsx";
import SearchResults, { ResultsMessage } from "../components/research/SearchResults.jsx";
import JudgmentDetail from "../components/research/JudgmentDetail.jsx";
import { useSearch } from "../hooks/useSearch.js";

const DEFAULT_K = 10;

export default function Research() {
  const [query, setQuery] = useState("");
  const [topK, setTopK] = useState(DEFAULT_K);
  const [selected, setSelected] = useState(null);
  const { status, data, error, errorKind, run, retry } = useSearch();
  const closeDetail = useCallback(() => setSelected(null), []);

  return (
    <PageContainer className="py-16 md:py-24">
      <header className="max-w-3xl">
        <h1 className="h-hero">Legal research</h1>
        <p className="mt-6 text-lg text-muted md:text-xl">Ask a legal question and retrieve relevant Supreme Court judgments.</p>
      </header>

      <div className="mt-12 max-w-4xl">
        <SearchForm query={query} topK={topK} onQueryChange={setQuery} onTopKChange={setTopK}
          onSubmit={() => run({ query, topK })} loading={status === "loading"}
          error={status === "error" && errorKind === "validation" ? error : null} />
      </div>

      <div className="mt-12 max-w-4xl">
        {status === "idle" && <p className="text-muted">Enter a legal question to begin research.</p>}
        {status === "loading" && <SearchLoading />}
        {status === "empty" && <ResultsMessage title="No relevant judgments were found for this query." body="Try rephrasing the question or referring to specific Articles or Sections." />}
        {status === "error" && errorKind === "service" && <ResultsMessage title="Research service is currently unavailable." body={error} onRetry={retry} />}
        {status === "success" && <SearchResults data={data} onViewDetails={setSelected} />}
      </div>

      <JudgmentDetail result={selected} onClose={closeDetail} />
    </PageContainer>
  );
}
