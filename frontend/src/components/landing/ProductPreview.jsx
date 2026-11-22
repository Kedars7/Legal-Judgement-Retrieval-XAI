import { motion } from "framer-motion";
import PageContainer from "../layout/PageContainer.jsx";
import SectionHeading from "../ui/SectionHeading.jsx";
import { mockSearchResponse } from "../../data/mockSearchResponse.js";
import { formatPercent, padRank } from "../../lib/utils.js";

export default function ProductPreview() {
  return (
    <section className="border-y border-black/10 bg-legal-white py-24 md:py-32">
      <PageContainer>
        <SectionHeading title="From question to evidence." description="Every result arrives with its rank, citation, relevance and the passage that supports it." />
        <div className="mt-16 grid gap-8 lg:grid-cols-5">
          <div className="lg:col-span-2">
            <div className="rounded-lg border border-black/10 bg-legal-paper p-6">
              <p className="text-sm font-medium text-muted">Legal query</p>
              <p className="mt-3 text-xl font-medium">Whether the State can restrict a fundamental right?</p>
              <div className="mt-6 flex items-center gap-4 text-sm text-muted"><span>Results: 3</span><span aria-hidden="true">·</span><span>Hybrid retrieval</span></div>
            </div>
          </div>
          <ol className="space-y-4 lg:col-span-3">
            {mockSearchResponse.results.map((r, i) => (
              <motion.li key={r.rank} initial={{ opacity: 0, y: 16 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }}
                transition={{ duration: 0.4, delay: i * 0.1 }} className="rounded-lg border border-black/10 bg-legal-paper p-6">
                <div className="flex items-start justify-between gap-4">
                  <div>
                    <p className="text-sm font-semibold text-legal-blue">{padRank(r.rank)}</p>
                    <h3 className="mt-1 text-xl font-semibold">{r.case.title}</h3>
                    <p className="mt-1 text-sm text-muted">{r.case.date} · {r.case.citation}</p>
                  </div>
                  <div className="text-right"><p className="text-xs text-muted">Relevance</p><p className="text-xl font-bold text-legal-blue">{formatPercent(r.relevance.model_score)}</p></div>
                </div>
                <blockquote className="mt-4 rounded-sm bg-legal-blue-tint px-4 py-3 text-base">{r.evidence}</blockquote>
              </motion.li>
            ))}
          </ol>
        </div>
      </PageContainer>
    </section>
  );
}
