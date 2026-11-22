import { Link } from "react-router-dom";
import { cn } from "../../lib/utils.js";

const base = "inline-flex items-center justify-center gap-2 rounded font-medium transition-colors duration-150 disabled:opacity-50 disabled:pointer-events-none";
const variants = {
  primary: "bg-legal-blue text-legal-white hover:bg-legal-blue-bright",
  secondary: "bg-legal-white text-legal-ink hairline hover:bg-legal-blue-tint",
  ghost: "text-legal-blue hover:bg-legal-blue-tint",
};
const sizes = { md: "h-10 px-4 text-base", lg: "h-12 px-6 text-lg" };

/** Renders <Link> when `to` is given, otherwise <button>. */
export default function Button({ variant = "primary", size = "md", to, className, children, ...props }) {
  const cls = cn(base, variants[variant], sizes[size], className);
  if (to) return <Link to={to} className={cls} {...props}>{children}</Link>;
  return <button className={cls} {...props}>{children}</button>;
}
