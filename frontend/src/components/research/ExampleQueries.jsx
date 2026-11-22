const EXAMPLES = [
  { label: "Article 14 protection", query: "Whether the accused is entitled to protection under Article 14 of the Constitution" },
  { label: "Preventive detention", query: "Validity of preventive detention and the safeguards available to a detained person" },
  { label: "Article 21 personal liberty", query: "Scope of the right to life and personal liberty under Article 21 of the Constitution" },
  { label: "Election writ petition", query: "Maintainability of a writ petition challenging an election result" },
];

export default function ExampleQueries({ onSelect, disabled }) {
  return (
    <div className="mt-6">
      <p className="text-sm font-medium text-muted">Try an example</p>
      <ul className="mt-3 flex flex-wrap gap-2">
        {EXAMPLES.map((e) => (
          <li key={e.label}>
            <button type="button" disabled={disabled} onClick={() => onSelect(e.query)}
              className="rounded border border-black/15 bg-legal-white px-3 py-2 text-sm font-medium transition-colors hover:bg-legal-blue-tint disabled:opacity-50">
              {e.label}
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}
