import { useRef, useState } from "react";
import { motion, useScroll, useSpring } from "framer-motion";
import PageContainer from "../layout/PageContainer.jsx";
import SectionHeading from "../ui/SectionHeading.jsx";
import { PIPELINE_STEPS } from "../../data/pipeline.js";
import { cn, padRank } from "../../lib/utils.js";

/** Vertical timeline: line draws with scroll, the step nearest the viewport centre is highlighted. */
export default function WorkflowPreview() {
  const ref = useRef(null);
  const [active, setActive] = useState(0);
  const { scrollYProgress } = useScroll({ target: ref, offset: ["start 70%", "end 60%"] });
  const progress = useSpring(scrollYProgress, { stiffness: 120, damping: 30 });

  return (
    <section className="border-y border-black/10 bg-legal-white py-24 md:py-32">
      <PageContainer className="grid gap-16 lg:grid-cols-5">
        <div className="lg:col-span-2">
          <div className="lg:sticky lg:top-32">
            <SectionHeading title="How the system works" description="Eight stages turn a plain-language question into ranked, explainable evidence." />
          </div>
        </div>
        <ol ref={ref} className="relative lg:col-span-3">
          <span className="absolute left-5 top-5 bottom-5 w-px bg-black/10" aria-hidden="true" />
          <motion.span className="absolute left-5 top-5 bottom-5 w-px origin-top bg-legal-blue" style={{ scaleY: progress }} aria-hidden="true" />
          {PIPELINE_STEPS.map((s, i) => (
            <motion.li key={s.id} onViewportEnter={() => setActive(i)} viewport={{ margin: "-45% 0px -45% 0px" }} className="relative flex gap-6 pb-12 last:pb-0">
              <span className={cn("z-10 flex h-10 w-10 shrink-0 items-center justify-center rounded-full border text-sm font-semibold transition-colors",
                i <= active ? "border-legal-blue bg-legal-blue text-legal-white" : "border-black/15 bg-legal-white text-black/60")}>{padRank(i + 1)}</span>
              <div className={cn("flex-1 rounded-lg border p-5 transition-colors", i === active ? "border-legal-blue bg-legal-blue-tint" : "border-black/10 bg-legal-paper")}>
                <h3 className="text-xl font-semibold">{s.title}</h3>
                <p className="mt-1 text-sm font-medium text-legal-blue">{s.tech}</p>
                <p className="mt-2 text-muted">{s.description}</p>
              </div>
            </motion.li>
          ))}
        </ol>
      </PageContainer>
    </section>
  );
}
