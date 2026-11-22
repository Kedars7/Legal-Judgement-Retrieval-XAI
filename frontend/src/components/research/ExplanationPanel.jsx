import { EXPLANATION_NOTE } from "../../data/pipeline.js";
import { formatSigned } from "../../lib/utils.js";

const MAX_ABS = 0.25; // bar scale: |contribution| of 0.25 fills the track

export function FactorList({ factors, tone }) {
  return (
    <ul>
      {factors.map(({ feature, value, description }) => (
        <li key={feature} title={description || undefined} className="flex items-center gap-4 py-2">
          <span className="w-40 shrink-0 text-sm md:w-52 md:text-base">{feature}{description && <span className="sr-only">. {description}</span>}</span>
          <div className="h-2 flex-1 rounded-sm bg-black/5" aria-hidden="true">
            <div className={tone === "positive" ? "h-2 rounded-sm bg-legal-blue" : "h-2 rounded-sm bg-black/40"}
              style={{ width: `${Math.min(Math.abs(value) / MAX_ABS, 1) * 100}%` }} />
          </div>
          <span className="w-14 text-right text-sm font-semibold tabular-nums">{formatSigned(value)}</span>
        </li>
      ))}
    </ul>
  );
}

export default function ExplanationPanel({ explanation }) {
  const { positive_factors = [], negative_factors = [] } = explanation ?? {};
  return (
    <div>
      {positive_factors.length > 0 && (
        <section aria-label="Positive contributions">
          <h4 className="text-sm font-semibold uppercase tracking-wider text-legal-blue">Positive contribution</h4>
          <FactorList factors={positive_factors} tone="positive" />
        </section>
      )}
      {negative_factors.length > 0 && (
        <section aria-label="Negative contributions" className="mt-6">
          <h4 className="text-sm font-semibold uppercase tracking-wider text-muted">Negative contribution</h4>
          <FactorList factors={negative_factors} tone="negative" />
        </section>
      )}
      <p className="mt-6 text-sm text-muted">{EXPLANATION_NOTE}</p>
    </div>
  );
}
