// Maps the FastAPI /search payload to the shape the UI consumes. Keep ALL backend-shape knowledge here.

/** Joins words split by PDF line-break hyphenation ("proceed- ings" -> "proceedings") and collapses whitespace. */
export const cleanEvidence = (text = "") => text.replace(/([a-z])- ([a-z])/g, "$1$2").replace(/\s+/g, " ").trim();

const normalizeFactor = (f) => ({
  feature: f.feature,
  value: f.contribution ?? f.value ?? 0, // backend sends `contribution`
  description: f.explanation ?? f.description ?? "",
});

export function normalizeResponse(data) {
  const results = (data.results ?? []).map((r) => ({
    ...r,
    evidence: cleanEvidence(r.evidence),
    explanation: {
      ...r.explanation,
      positive_factors: (r.explanation?.positive_factors ?? []).map(normalizeFactor),
      negative_factors: (r.explanation?.negative_factors ?? []).map(normalizeFactor),
      feature_values: r.explanation?.feature_values ?? {},
    },
  }));
  return { ...data, results, total_results: data.total_results ?? results.length };
}
