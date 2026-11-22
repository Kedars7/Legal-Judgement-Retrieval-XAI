import PageContainer from "../components/layout/PageContainer.jsx";
import Card from "../components/ui/Card.jsx";
import { DISCLAIMER } from "../lib/utils.js";

const TECH = [
  ["InLegalBERT", "Legal-domain embeddings for semantic matching."],
  ["FAISS", "Vector similarity search over judgment chunks."],
  ["BM25", "Lexical matching for exact legal terms and references."],
  ["Reciprocal Rank Fusion", "Merges semantic and lexical rankings."],
  ["Random Forest", "Scores candidate relevance from retrieval signals."],
  ["SHAP", "Explains feature contributions to the relevance score."],
  ["FastAPI", "Python service exposing the search endpoint."],
  ["React + Tailwind CSS", "The interface you are using."],
];

export default function About() {
  return (
    <PageContainer className="py-16 md:py-24">
      <h1 className="h-hero max-w-4xl">Built for explainable legal research.</h1>
      <p className="mt-8 max-w-2xl text-lg text-muted md:text-xl">
        This project explores how modern information retrieval and explainable AI can help users find relevant Indian Supreme Court judgments.
      </p>
      <ul className="mt-16 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {TECH.map(([name, text]) => (
          <li key={name}><Card interactive className="h-full p-6"><h2 className="text-lg font-semibold">{name}</h2><p className="mt-2 text-muted">{text}</p></Card></li>
        ))}
      </ul>
      <p className="mt-12 text-sm text-muted">{DISCLAIMER}</p>
    </PageContainer>
  );
}
