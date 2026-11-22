import { mockSearchResponse } from "../data/mockSearchResponse.js";
import { normalizeResponse } from "./normalizeResponse.js";

/** Mock mode is the default. Set VITE_USE_MOCK_DATA=false to call the FastAPI backend. */
const USE_MOCK_DATA = import.meta.env.VITE_USE_MOCK_DATA !== "false";
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000";
const MOCK_LATENCY_MS = 3200; // long enough to show the staged loading UI

export class SearchError extends Error {
  constructor(message, kind = "unavailable") {
    super(message);
    this.kind = kind; // "unavailable" | "server" | "aborted"
  }
}

const sleep = (ms, signal) =>
  new Promise((resolve, reject) => {
    const t = setTimeout(resolve, ms);
    signal?.addEventListener("abort", () => { clearTimeout(t); reject(new SearchError("Aborted", "aborted")); });
  });

/** POST /search  { query, top_k } */
export async function searchJudgments({ query, topK }, signal) {
  if (USE_MOCK_DATA) {
    await sleep(MOCK_LATENCY_MS, signal);
    const results = mockSearchResponse.results.slice(0, topK);
    return normalizeResponse({ ...mockSearchResponse, query, results, total_results: results.length });
  }

  let res;
  try {
    res = await fetch(`${API_BASE_URL}/search`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query, top_k: topK }),
      signal,
    });
  } catch (err) {
    if (err.name === "AbortError") throw new SearchError("Aborted", "aborted");
    throw new SearchError("Research service is currently unavailable.", "unavailable");
  }
  if (!res.ok) throw new SearchError(`Search failed (HTTP ${res.status}).`, "server");
  try {
    return normalizeResponse(await res.json());
  } catch {
    throw new SearchError("Received an unexpected response from the research service.", "server");
  }
}
