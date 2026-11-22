import { cn } from "../../lib/utils.js";

const tones = {
  neutral: "bg-legal-white hairline text-black/70",
  blue: "bg-legal-blue-tint text-legal-blue",
  teal: "bg-legal-teal text-legal-ink",
};

export default function Badge({ tone = "neutral", className, children }) {
  return <span className={cn("inline-flex items-center rounded-sm px-2 py-1 text-sm font-medium", tones[tone], className)}>{children}</span>;
}
