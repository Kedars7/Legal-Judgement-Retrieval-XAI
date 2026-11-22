import { cn } from "../../lib/utils.js";

export default function SectionHeading({ eyebrow, title, description, as: Tag = "h2", action, className }) {
  return (
    <div className={cn("flex flex-col gap-6 md:flex-row md:items-end md:justify-between", className)}>
      <div className="max-w-3xl">
        {eyebrow && <p className="mb-4 text-sm font-semibold uppercase tracking-wider text-legal-blue">{eyebrow}</p>}
        <Tag className="h-section">{title}</Tag>
        {description && <p className="mt-6 text-lg text-muted md:text-xl">{description}</p>}
      </div>
      {action}
    </div>
  );
}
