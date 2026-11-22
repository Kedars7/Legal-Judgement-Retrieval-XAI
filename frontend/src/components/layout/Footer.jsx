import { Link } from "react-router-dom";
import { Scale } from "lucide-react";
import PageContainer from "./PageContainer.jsx";
import { DISCLAIMER } from "../../lib/utils.js";

export default function Footer() {
  return (
    <footer className="mt-32 border-t border-black/10 bg-legal-white">
      <PageContainer className="grid gap-12 py-16 md:grid-cols-3">
        <div>
          <p className="flex items-center gap-2 text-lg font-semibold">
            <Scale size={20} className="text-legal-blue" aria-hidden="true" /> Legal Research AI
          </p>
          <p className="mt-4 max-w-xs text-muted">Explainable retrieval over Indian Supreme Court judgments.</p>
        </div>
        <nav aria-label="Footer" className="flex flex-col gap-3">
          <Link to="/research" className="hover:text-legal-blue">Research</Link>
          <Link to="/how-it-works" className="hover:text-legal-blue">How it works</Link>
          <Link to="/about" className="hover:text-legal-blue">About</Link>
        </nav>
        <p className="text-sm text-muted">{DISCLAIMER}</p>
      </PageContainer>
    </footer>
  );
}
