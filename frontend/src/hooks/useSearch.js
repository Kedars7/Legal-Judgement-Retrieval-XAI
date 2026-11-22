import { useCallback, useRef, useState } from "react";
import { searchJudgments, SearchError } from "../api/searchApi.js";
import { MIN_QUERY_LENGTH } from "../lib/utils.js";

/**
 * status: idle | loading | success | empty | error
 * errorKind: "validation" (fix the input) | "service" (retry is useful)
 */
export function useSearch() {
  const [state, setState] = useState({ status: "idle", data: null, error: null, errorKind: null });
  const lastParams = useRef(null);
  const controller = useRef(null);

  const fail = (error, errorKind) => setState({ status: "error", data: null, error, errorKind });

  const run = useCallback(async ({ query, topK }) => {
    const trimmed = query.trim();
    if (!trimmed) return fail("Enter a legal question to begin research.", "validation");
    if (trimmed.length < MIN_QUERY_LENGTH) return fail("Please enter a more detailed legal question.", "validation");

    controller.current?.abort();
    controller.current = new AbortController();
    lastParams.current = { query: trimmed, topK };
    setState({ status: "loading", data: null, error: null, errorKind: null });

    try {
      const data = await searchJudgments(lastParams.current, controller.current.signal);
      setState({ status: data.results?.length ? "success" : "empty", data, error: null, errorKind: null });
    } catch (err) {
      if (err instanceof SearchError && err.kind === "aborted") return;
      fail(err.message || "Research service is currently unavailable.", "service");
    }
  }, []);

  const retry = useCallback(() => { if (lastParams.current) run(lastParams.current); }, [run]);
  return { ...state, run, retry };
}
