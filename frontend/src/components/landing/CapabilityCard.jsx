import Card from "../ui/Card.jsx";
import { cn } from "../../lib/utils.js";

export default function CapabilityCard({ title, description, visual, surface = "bg-legal-blue-tint" }) {
  return (
    <Card as="article" interactive className="flex h-full flex-col overflow-hidden">
      <div className={cn("h-52 border-b border-black/10", surface)}>{visual}</div>
      <div className="flex flex-1 flex-col p-6">
        <h3 className="text-2xl font-semibold tracking-tight">{title}</h3>
        <p className="mt-3 text-base text-muted md:text-lg">{description}</p>
      </div>
    </Card>
  );
}
