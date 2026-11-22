import { useEffect, useState } from "react";
import { AnimatePresence, motion, useReducedMotion } from "framer-motion";
import { BarChart3, Cpu, FileText, Gauge, GitMerge, Network, Pause, Play, Search, Type } from "lucide-react";
import PipelineStep from "./PipelineStep.jsx";
import { PIPELINE_STAGES } from "../../data/pipeline.js";
import { cn } from "../../lib/utils.js";

const ICONS = [Type, Cpu, Network, Search, GitMerge, Gauge, BarChart3, FileText];
const AUTOPLAY_MS = 2200;
const LAST = PIPELINE_STAGES.length - 1;

/** Interactive pipeline. A "data packet" travels the track while autoplay runs; hover/click selects a stage and pauses autoplay. */
export default function Pipeline() {
  const reduce = useReducedMotion();
  const [active, setActive] = useState(0);
  const [playing, setPlaying] = useState(!reduce);

  useEffect(() => {
    if (!playing) return;
    const t = setInterval(() => setActive((a) => (a >= LAST ? 0 : a + 1)), AUTOPLAY_MS);
    return () => clearInterval(t);
  }, [playing]);

  const select = (i) => { setActive(i); setPlaying(false); };
  const stage = PIPELINE_STAGES[active];
  const pct = (active / LAST) * 100;

  return (
    <div>
      <div className="mb-6 flex items-center gap-4">
        <div className="relative hidden h-1 flex-1 rounded-sm bg-black/10 lg:block" aria-hidden="true">
          <motion.div className="absolute left-0 top-0 h-1 rounded-sm bg-legal-blue" animate={{ width: `${pct}%` }} transition={{ duration: 0.6 }} />
          <motion.div className="absolute top-1/2 h-3 w-3 -translate-x-1/2 -translate-y-1/2 rounded-full bg-legal-blue-bright" animate={{ left: `${pct}%` }} transition={{ duration: 0.6 }} />
        </div>
        <button type="button" onClick={() => setPlaying((p) => !p)} aria-pressed={playing}
          className="inline-flex h-10 shrink-0 items-center gap-2 rounded border border-black/15 bg-legal-white px-3 text-sm font-medium hover:bg-legal-blue-tint">
          {playing ? <Pause size={16} aria-hidden="true" /> : <Play size={16} aria-hidden="true" />}
          {playing ? "Pause data flow" : "Play data flow"}
        </button>
      </div>

      {/* Mobile: single-column list with a vertical rail. Desktop: 4-column grid. */}
      <ol className="relative grid gap-4 max-lg:border-l max-lg:border-black/10 max-lg:pl-4 sm:grid-cols-2 lg:grid-cols-4">
        {PIPELINE_STAGES.map((s, i) => (
          <motion.li key={s.id} initial={{ opacity: 0, y: 12 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ delay: (i % 4) * 0.06 }}>
            <PipelineStep index={i} stage={s} Icon={ICONS[i]} active={i === active} onSelect={select} />
          </motion.li>
        ))}
      </ol>

      <div className="mt-8 rounded-lg border border-black/10 bg-legal-white p-6 md:p-10" aria-live="polite">
        <AnimatePresence mode="wait">
          <motion.div key={stage.id} initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }} transition={{ duration: 0.2 }}>
            <p className="text-sm font-semibold uppercase tracking-wider text-legal-blue">Stage {String(active + 1).padStart(2, "0")}</p>
            <h3 className="mt-2 text-3xl font-bold tracking-tight">{stage.title}</h3>
            <dl className="mt-6 grid gap-6 md:grid-cols-4">
              {[["Technology", stage.tech], ["Purpose", stage.purpose], ["Input", stage.input], ["Output", stage.output]].map(([k, v], i) => (
                <div key={k} className={cn(i === 1 && "md:col-span-2")}>
                  <dt className="text-sm text-muted">{k}</dt>
                  <dd className="mt-1 text-base font-medium">{v}</dd>
                </div>
              ))}
            </dl>
          </motion.div>
        </AnimatePresence>
      </div>
    </div>
  );
}
