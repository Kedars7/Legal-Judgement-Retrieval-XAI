import { useEffect, useRef, useId } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { X } from "lucide-react";

/** Accessible drawer dialog: ESC closes, Tab is cycled inside, focus returns to trigger, body scroll locked. */
export default function Modal({ open, onClose, title, children }) {
  const panelRef = useRef(null);
  const titleId = useId();

  useEffect(() => {
    if (!open) return;
    const previous = document.activeElement;
    document.body.style.overflow = "hidden";
    const focusables = () => panelRef.current?.querySelectorAll('button,[href],input,select,textarea,[tabindex]:not([tabindex="-1"])') ?? [];
    requestAnimationFrame(() => focusables()[0]?.focus());

    const onKey = (e) => {
      if (e.key === "Escape") return onClose();
      if (e.key !== "Tab") return;
      const els = [...focusables()];
      if (!els.length) return;
      const first = els[0], last = els[els.length - 1];
      if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
      else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
    };
    document.addEventListener("keydown", onKey);
    return () => {
      document.removeEventListener("keydown", onKey);
      document.body.style.overflow = "";
      previous?.focus?.();
    };
  }, [open, onClose]);

  return (
    <AnimatePresence>
      {open && (
        <div className="fixed inset-0 z-50 flex justify-end">
          <motion.div className="absolute inset-0 bg-black/30" onClick={onClose}
            initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} aria-hidden="true" />
          <motion.div
            ref={panelRef} role="dialog" aria-modal="true" aria-labelledby={titleId}
            className="relative flex h-full w-full max-w-2xl flex-col overflow-y-auto bg-legal-paper"
            initial={{ x: 40, opacity: 0 }} animate={{ x: 0, opacity: 1 }} exit={{ x: 40, opacity: 0 }}
            transition={{ duration: 0.2 }}
          >
            <div className="sticky top-0 z-10 flex items-start justify-between gap-4 border-b border-black/10 bg-legal-paper px-6 py-5">
              <h2 id={titleId} className="text-xl font-semibold">{title}</h2>
              <button onClick={onClose} aria-label="Close dialog" className="rounded p-2 hover:bg-legal-blue-tint">
                <X size={20} />
              </button>
            </div>
            <div className="p-6">{children}</div>
          </motion.div>
        </div>
      )}
    </AnimatePresence>
  );
}
