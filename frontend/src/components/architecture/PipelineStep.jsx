import { cn, padRank } from "../../lib/utils.js";

export default function PipelineStep({ index, stage, Icon, active, onSelect }) {
  return (
    <button type="button" onClick={() => onSelect(index)} onMouseEnter={() => onSelect(index, true)} onFocus={() => onSelect(index, true)}
      aria-pressed={active}
      className={cn("h-full w-full rounded-lg border p-5 text-left transition-colors",
        active ? "border-legal-blue bg-legal-blue-tint" : "border-black/10 bg-legal-white hover:border-black/25")}>
      <div className="flex items-center justify-between">
        <span className={cn("text-sm font-semibold", active ? "text-legal-blue" : "text-muted")}>{padRank(index + 1)}</span>
        <Icon size={20} className={active ? "text-legal-blue" : "text-black/50"} aria-hidden="true" />
      </div>
      <h3 className="mt-6 text-lg font-semibold leading-snug">{stage.title}</h3>
      <p className="mt-1 text-sm font-medium text-legal-blue">{stage.tech}</p>
      <p className="mt-3 text-sm text-muted">{stage.description}</p>
    </button>
  );
}
