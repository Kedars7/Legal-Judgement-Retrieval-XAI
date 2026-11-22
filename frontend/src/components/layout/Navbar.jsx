import { useEffect, useState } from "react";
import { NavLink, Link, useLocation } from "react-router-dom";
import { AnimatePresence, motion } from "framer-motion";
import { Menu, Scale, X } from "lucide-react";
import PageContainer from "./PageContainer.jsx";
import Button from "../ui/Button.jsx";
import { cn } from "../../lib/utils.js";

const LINKS = [
  { to: "/research", label: "Research" },
  { to: "/how-it-works", label: "How it works" },
  { to: "/about", label: "About" },
];

const linkClass = ({ isActive }) =>
  cn("rounded px-3 py-2 text-base font-medium transition-colors hover:bg-legal-blue-tint", isActive ? "text-legal-blue" : "text-legal-ink");

export default function Navbar() {
  const [open, setOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);
  const { pathname } = useLocation();

  useEffect(() => setOpen(false), [pathname]);
  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 8);
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);
  useEffect(() => {
    if (!open) return;
    const onKey = (e) => e.key === "Escape" && setOpen(false);
    document.addEventListener("keydown", onKey);
    return () => document.removeEventListener("keydown", onKey);
  }, [open]);

  return (
    <header className={cn("sticky top-0 z-40 bg-legal-paper/95 backdrop-blur-sm transition-colors", scrolled ? "border-b border-black/10" : "border-b border-transparent")}>
      <PageContainer className="flex h-16 items-center justify-between">
        <Link to="/" className="flex items-center gap-2 text-lg font-semibold" aria-label="Legal Research AI — home">
          <Scale size={22} className="text-legal-blue" aria-hidden="true" />
          Legal Research AI
        </Link>

        <nav aria-label="Primary" className="hidden items-center gap-2 md:flex">
          {LINKS.map((l) => <NavLink key={l.to} to={l.to} className={linkClass}>{l.label}</NavLink>)}
          <Button to="/research" className="ml-4">Try Research</Button>
        </nav>

        <button
          className="rounded p-2 hover:bg-legal-blue-tint md:hidden"
          aria-label={open ? "Close menu" : "Open menu"} aria-expanded={open} aria-controls="mobile-nav"
          onClick={() => setOpen((o) => !o)}
        >
          {open ? <X size={24} /> : <Menu size={24} />}
        </button>
      </PageContainer>

      <AnimatePresence>
        {open && (
          <motion.nav
            id="mobile-nav" aria-label="Mobile"
            initial={{ height: 0, opacity: 0 }} animate={{ height: "auto", opacity: 1 }} exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="overflow-hidden border-t border-black/10 bg-legal-paper md:hidden"
          >
            <PageContainer className="flex flex-col gap-1 py-4">
              {LINKS.map((l) => <NavLink key={l.to} to={l.to} className={(s) => cn(linkClass(s), "text-lg")}>{l.label}</NavLink>)}
              <Button to="/research" size="lg" className="mt-3">Try Research</Button>
            </PageContainer>
          </motion.nav>
        )}
      </AnimatePresence>
    </header>
  );
}
