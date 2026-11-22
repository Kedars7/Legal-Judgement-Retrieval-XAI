import { useEffect, useState } from "react";
import { Check } from "lucide-react";
import { cn } from "../../lib/utils.js";

const STEPS = ["Analyzing query", "Searching semantic index", "Matching legal terms", "Combining rankings", "Generating explanations"];
const STEP_MS = 650;

/** Steps advance on a timer (purely presentational) and hold on the last step until results arrive. */
export default function SearchLoading() {
  const [current, setCurrent] = useState(0);
  useEffect(() => {
    const t = setInterval(() => setCurrent((c) => Math.min(c + 1, STEPS.length - 1)), STEP_MS);
    return () => clearInterval(t);
  }, []);

  return (
    <div className="rounded-lg border border-black/10 bg-legal-white p-6 md:p-10" aria-busy="true">
      <p role="status" aria-live="polite" className="sr-only">{STEPS[current]}</p>
      <ol className="space-y-5">
        {STEPS.map((s, i) => {
          const done = i < current, active = i === current;
          return (
            <li key={s} className={cn("flex items-center gap-4 transition-opacity", i > current && "opacity-40")}>
              <span className={cn("flex h-8 w-8 items-center justify-center rounded-full border text-sm",
                done ? "border-legal-blue bg-legal-blue text-legal-white" : active ? "border-legal-blue text-legal-blue" : "border-black/20")}>
                {done ? <Check size={16} aria-hidden="true" /> : i + 1}
              </span>
              <span className={cn("text-lg", active ? "font-semibold" : "font-medium")}>{s}{active && <span className="animate-pulse">…</span>}</span>
            </li>
          );
        })}
      </ol>
    </div>
  );
}
