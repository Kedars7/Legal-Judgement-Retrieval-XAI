// Sample data matching the FastAPI /search contract. Excerpts are illustrative placeholders.
export const mockSearchResponse = {
  query: "Whether the accused is entitled to protection under Article 14 of the Constitution",
  retrieval: { dense_top_k: 50, bm25_top_k: 50, max_chunks_per_judgment: 2, rrf_constant: 60 },
  results: [
    {
      rank: 1,
      case: { title: "Ramjilal vs Income Tax Officer Mohindargarh", date: "14/05/1951", citation: "1951 AIR 97, 1951 SCR 127", bench: "Supreme Court of India", petitioner: "Ramjilal", respondent: "Income Tax Officer, Mohindargarh" },
      retrieval: { rrf_score: 0.0288, dense_score: 0.7655, dense_rank: 7, bm25_score: 28.04, bm25_rank: 12 },
      relevance: { model_score: 0.8723, prediction: 1 },
      explanation: {
        positive_factors: [
          { feature: "Hybrid RRF Score", value: 0.21 },
          { feature: "Legal Reference Match", value: 0.08 },
          { feature: "Article Overlap", value: 0.06 },
          { feature: "BM25 Score", value: 0.06 },
        ],
        negative_factors: [
          { feature: "Dense Similarity", value: -0.03 },
          { feature: "Keyword Overlap", value: -0.01 },
        ],
        feature_values: { rrf_score: 0.0288, dense_score: 0.7655, bm25_score: 28.04, article_overlap: 1 },
      },
      evidence: "...the guarantee of equal protection of the laws under Article 14 forbids class legislation but does not forbid reasonable classification...",
    },
    {
      rank: 2,
      case: { title: "Budhan Choudhry vs State of Bihar", date: "20/10/1954", citation: "1955 AIR 191, 1955 SCR (1)1045", bench: "Supreme Court of India", petitioner: "Budhan Choudhry and Others", respondent: "State of Bihar" },
      retrieval: { rrf_score: 0.0271, dense_score: 0.7412, dense_rank: 4, bm25_score: 24.9, bm25_rank: 15 },
      relevance: { model_score: 0.8164, prediction: 1 },
      explanation: {
        positive_factors: [
          { feature: "Hybrid RRF Score", value: 0.18 },
          { feature: "Article Overlap", value: 0.07 },
          { feature: "Legal Reference Match", value: 0.05 },
        ],
        negative_factors: [{ feature: "BM25 Score", value: -0.02 }],
        feature_values: { rrf_score: 0.0271, dense_score: 0.7412, bm25_score: 24.9, article_overlap: 1 },
      },
      evidence: "...classification must be founded on an intelligible differentia and must bear a rational relation to the object sought to be achieved...",
    },
    {
      rank: 3,
      case: { title: "Baburao Shantaram More vs Bombay Housing Board", date: "1954", citation: "1954 AIR 153, 1954 SCR 572", bench: "Supreme Court of India", petitioner: "Baburao Shantaram More", respondent: "Bombay Housing Board" },
      retrieval: { rrf_score: 0.0243, dense_score: 0.7021, dense_rank: 11, bm25_score: 21.3, bm25_rank: 9 },
      relevance: { model_score: 0.7412, prediction: 1 },
      explanation: {
        positive_factors: [
          { feature: "Hybrid RRF Score", value: 0.14 },
          { feature: "BM25 Score", value: 0.05 },
        ],
        negative_factors: [
          { feature: "Dense Similarity", value: -0.04 },
          { feature: "Article Overlap", value: -0.02 },
        ],
        feature_values: { rrf_score: 0.0243, dense_score: 0.7021, bm25_score: 21.3, article_overlap: 0 },
      },
      evidence: "...the State is not precluded from making a reasonable classification for the purpose of legislation under Article 14...",
    },
  ],
  total_results: 3,
};
