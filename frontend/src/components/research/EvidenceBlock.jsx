import { useId, useState } from "react";
import { cn } from "../../lib/utils.js";

const PREVIEW_CHARS = 320;

/** Long passages are clipped to a preview with an expand toggle. Clips at a word boundary. */
export default function EvidenceBlock({ text, label = "Evidence", collapsible = true, className }) {
  const [expanded, setExpanded] = useState(false);
  const id = useId();
  if (!text) return null;

  const long = collapsible && text.length > PREVIEW_CHARS;
  const shown = long && !expanded ? `${text.slice(0, PREVIEW_CHARS).replace(/\s+\S*$/, "")}…` : text;

  return (
    <figure className={cn("rounded bg-legal-blue-tint px-4 py-3", className)}>
      <figcaption className="text-xs font-semibold uppercase tracking-wider text-legal-blue">{label}</figcaption>
      <blockquote id={id} className="mt-2 text-base leading-relaxed">{shown}</blockquote>
      {long && (
        <button type="button" onClick={() => setExpanded((e) => !e)} aria-expanded={expanded} aria-controls={id}
          className="mt-2 rounded text-sm font-medium text-legal-blue hover:underline">
          {expanded ? "Show less" : "Read full passage"}
        </button>
      )}
    </figure>
  );
}
