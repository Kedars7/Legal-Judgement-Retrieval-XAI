import { Search } from "lucide-react";
import Button from "../ui/Button.jsx";
import ExampleQueries from "./ExampleQueries.jsx";
import { K_OPTIONS } from "../../lib/utils.js";

export default function SearchForm({ query, topK, onQueryChange, onTopKChange, onSubmit, loading, error }) {
  return (
    <form onSubmit={(e) => { e.preventDefault(); onSubmit(); }} noValidate className="rounded-lg border border-black/10 bg-legal-white p-5 md:p-8">
      <label htmlFor="query" className="block text-base font-semibold">Legal question</label>
      <textarea
        id="query" rows={4} value={query} onChange={(e) => onQueryChange(e.target.value)}
        aria-invalid={!!error} aria-describedby={error ? "query-error" : undefined}
        placeholder="e.g. Whether the accused is entitled to protection under Article 14 of the Constitution"
        className="mt-3 w-full resize-y rounded border border-black/15 bg-legal-paper p-4 text-lg placeholder:text-black/40"
      />
      {error && <p id="query-error" role="alert" className="mt-2 text-sm font-medium text-legal-blue">{error}</p>}

      <div className="mt-6 flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <label htmlFor="top-k" className="block text-sm font-semibold">Number of results</label>
          <select id="top-k" value={topK} onChange={(e) => onTopKChange(Number(e.target.value))}
            className="mt-2 h-12 w-full rounded border border-black/15 bg-legal-white px-3 text-base sm:w-40">
            {K_OPTIONS.map((k) => <option key={k} value={k}>{k}</option>)}
          </select>
        </div>
        <Button type="submit" size="lg" disabled={loading}><Search size={18} aria-hidden="true" />{loading ? "Searching…" : "Search judgments"}</Button>
      </div>
      <ExampleQueries onSelect={onQueryChange} disabled={loading} />
    </form>
  );
}
