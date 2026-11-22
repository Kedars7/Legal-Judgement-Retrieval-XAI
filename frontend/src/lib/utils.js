export const cn = (...parts) => parts.filter(Boolean).join(" ");
export const formatPercent = (score, digits = 1) => `${(score * 100).toFixed(digits)}%`;
export const formatSigned = (n, digits = 2) => `${n >= 0 ? "+" : "−"}${Math.abs(n).toFixed(digits)}`;
export const padRank = (n) => String(n).padStart(2, "0");

export const MIN_QUERY_LENGTH = 15;
export const K_OPTIONS = [5, 10, 15, 20];
export const DISCLAIMER = "Research assistance only. Retrieved results do not constitute legal advice.";
