// Single source of truth for pipeline stages (landing preview + How it works page).
export const PIPELINE_STEPS = [
  { id: "query", title: "User query", tech: "Natural language", description: "A legal question is cleaned and prepared for retrieval." },
  { id: "embed", title: "InLegalBERT", tech: "Transformer embeddings", description: "The query is encoded into a legal-domain semantic vector." },
  { id: "faiss", title: "FAISS semantic search", tech: "FAISS", description: "Judgment chunks with similar embeddings are retrieved." },
  { id: "bm25", title: "BM25 search", tech: "BM25", description: "Exact legal terms and references are matched lexically." },
  { id: "rrf", title: "RRF hybrid ranking", tech: "Reciprocal Rank Fusion", description: "Semantic and lexical rankings are merged into one list." },
  { id: "rf", title: "Relevance model", tech: "Random Forest", description: "Each candidate is scored for relevance from its retrieval signals." },
  { id: "shap", title: "SHAP explanation", tech: "SHAP", description: "Feature contributions show how the relevance model scored each result." },
  { id: "evidence", title: "Ranked evidence", tech: "Judgment passages", description: "Ranked judgments are returned with supporting passages." },
];

export const EXPLANATION_NOTE =
  "These explanations describe how the retrieval relevance model contributed to the result. They do not explain a court's reasoning.";

// Detailed stages for the interactive How it works pipeline. Numbers come from the API's `retrieval` block (top 50 / 2 chunks).
export const PIPELINE_STAGES = [
  { id: "query", title: "Query Processing", tech: "Natural language", description: "The legal question is cleaned and prepared.", purpose: "Turn the user's question into text the retrieval components can use.", input: "Legal question", output: "Normalised query text" },
  { id: "embed", title: "Legal Embedding", tech: "InLegalBERT", description: "The query becomes a legal-domain vector.", purpose: "Capture the meaning of the query using a model trained on Indian legal text.", input: "Query text", output: "Query embedding" },
  { id: "faiss", title: "Semantic Retrieval", tech: "FAISS", description: "Similar judgment chunks are found by vector search.", purpose: "Find judgment chunks whose embeddings are semantically similar to the query.", input: "Query embedding", output: "Top 50 semantic candidates" },
  { id: "bm25", title: "Lexical Retrieval", tech: "BM25", description: "Exact terms and references are matched.", purpose: "Find chunks that share the query's specific legal terms, Articles and Sections.", input: "Query text", output: "Top 50 lexical candidates" },
  { id: "rrf", title: "Hybrid Ranking", tech: "Reciprocal Rank Fusion", description: "Two rankings are merged into one.", purpose: "Combine semantic and lexical ranks so a result strong in either list rises.", input: "Semantic + lexical rankings", output: "Fused ranking (max 2 chunks per judgment)" },
  { id: "rf", title: "Relevance Scoring", tech: "Random Forest", description: "Candidates are scored from their retrieval signals.", purpose: "Estimate how relevant each candidate is using retrieval features such as scores and reference overlap.", input: "Retrieval features per candidate", output: "Relevance score and prediction" },
  { id: "shap", title: "Explainability", tech: "SHAP", description: "Feature contributions are computed.", purpose: "Show how each feature contributed to the relevance model's score. This does not explain a court's reasoning.", input: "Relevance model + features", output: "Positive and negative contributions" },
  { id: "evidence", title: "Evidence", tech: "Retrieved judgment passage", description: "The supporting passage is returned.", purpose: "Show the judgment text that supports each retrieved result.", input: "Ranked judgments", output: "Ranked results with evidence" },
];

export const IMPLEMENTATION_DETAILS = [
  ["Corpus", "Indian Supreme Court judgments"],
  ["Processing", "PDF extraction, cleaning, chunking"],
  ["Embeddings", "InLegalBERT"],
  ["Vector search", "FAISS"],
  ["Lexical search", "BM25"],
  ["Hybrid ranking", "Reciprocal Rank Fusion"],
  ["Relevance model", "Random Forest"],
  ["Explainability", "SHAP"],
  ["Backend", "Python + FastAPI"],
  ["Frontend", "React + Tailwind CSS"],
];
