import { motion } from "framer-motion";
import { cn } from "../../lib/utils.js";

/** Flat editorial card. `interactive` adds the subtle hover lift. */
export default function Card({ as = "div", interactive = false, className, children, ...props }) {
  const Comp = motion[as] ?? motion.div;
  return (
    <Comp
      whileHover={interactive ? { y: -2 } : undefined}
      transition={{ duration: 0.15 }}
      className={cn("rounded-lg bg-legal-white hairline", interactive && "hover:border-black/20", className)}
      {...props}
    >
      {children}
    </Comp>
  );
}
