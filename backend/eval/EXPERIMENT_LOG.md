# Legal Judgment Retrieval and Explainable AI
# Experimental Evaluation Log

## Experiment 0: Initial Evaluation Dataset Verification

### Objective
Verify the availability and structure of the labeled dataset required for retrieval and relevance-model evaluation.

### Dataset Details
- Dataset file: `eval/relevance_dataset_labeled.csv`
- Total query-candidate pairs: 200
- Unique queries: 20
- Relevant candidates (label 1): 82
- Non-relevant candidates (label 0): 118
- Relevant candidate proportion: 41%
- Non-relevant candidate proportion: 59%

### Available Features
- Dense similarity score and rank
- BM25 score and rank
- Reciprocal Rank Fusion (RRF) score
- Keyword overlap
- Query-term coverage
- Article, section, and legal-reference overlap
- Matched keywords and legal references
- Judgment evidence text
- Relevance label and labeling rationale

### Initial Verification
- The dataset contains 200 rows and 23 columns.
- The dataset covers 20 queries.
- Relevance labels are binary: 0 and 1.
- The dataset is available for subsequent evaluation.

### Important Limitation
These 200 candidates were collected from hybrid retrieval. They do not independently establish the relevance of every judgment that semantic-only or BM25-only retrieval might return. A separate pooled candidate evaluation will be created for a fair comparison of retrieval methods.

### Status
Completed: initial dataset verification.
Pending: comparative retrieval experiments and quantitative evaluation.

### Evidence to Preserve
- Terminal output showing dataset dimensions and label distribution.
- A copy of the labeled CSV.
- Git commit or code version used for each experiment, where available.



## Experiment 3.1 — Label Coverage Diagnostic

### Objective
Verify retrieval-result integrity and measure the coverage of the existing relevance labels across semantic, BM25, and hybrid retrieval.

### Results
- Retrieval output: 600 rows, with 200 results per method.
- Duplicate query/chunk keys within individual retrieval methods: 0.
- Duplicate query/chunk keys in the relevance dataset: 1 duplicated pair.
- Conflicting relevance labels for the same query/chunk key: 0.
- Missing query IDs or chunk IDs: 0.

### Label Coverage

| Method | Total Results | Labeled | Unlabeled |
|---     |---:           |---:     |---:       |
| Semantic | 200         | 77 | 123 |
| BM25 | 200 | 76        | 124 |
| Hybrid RRF | 200       | 199 | 1 |

### Interpretation
The existing relevance labels provide nearly complete coverage of hybrid results but insufficient coverage of semantic and BM25 results. The labeled subsets are therefore not directly comparable for final retrieval-quality evaluation.

The duplicate label key was removed in memory for the diagnostic merge. The original dataset was not modified.

### Next Steps
Create a pooled candidate set across all three methods, resolve duplicate query/chunk keys, assign relevance judgments to previously unlabeled candidates, and evaluate all methods against the same judgments.

### Status
Completed: result-integrity and label-coverage diagnostics.

Pending: pooled relevance judgments and fair comparative retrieval evaluation.




### Experiment: Pooled Retrieval Method Comparison

**Objective:** Compare semantic retrieval, BM25 lexical retrieval, and hybrid Reciprocal Rank Fusion (RRF) for retrieving relevant passages from the legal judgment corpus.

**Dataset and configuration**
- Evaluation queries: 20
- Ranked results: 600 (200 per retrieval method)
- Unique pooled candidates: 445
- Relevant judgments: 149
- Non-relevant judgments: 296
- Dense candidate depth: 50
- BM25 candidate depth: 50
- RRF constant: 60
- Final ranking depth: 10
- Maximum chunks per judgment: 2

**Results**

| Metric | Semantic | BM25 | Hybrid RRF |
|---|---:|---:|---:|
| Precision@5 | 0.2600 | 0.5600 | 0.5800 |
| Precision@10 | 0.2300 | 0.4600 | 0.4100 |
| Recall@10 | 0.2759 | 0.6307 | 0.5519 |
| MAP@10 | 0.1524 | 0.4965 | 0.4569 |
| nDCG@10 | 0.2752 | 0.6488 | 0.5959 |
| MRR | 0.4167 | 0.7917 | 0.7696 |

**Observations**

BM25 achieved the highest scores on five of the six reported metrics. Hybrid RRF achieved the highest Precision@5, with a score of 0.5800. Semantic retrieval recorded the lowest scores across all six metrics.

**Conclusion**

Under the current experimental configuration and pooled relevance judgments, BM25 outperformed hybrid RRF and semantic retrieval on most ranking metrics. The hybrid method's performance indicates that combining lexical and dense rankings did not consistently improve retrieval quality. Further investigation is needed to understand the contribution of each component and identify opportunities to improve fusion.

**Limitations**

The evaluation contains 20 queries, and relevance annotations were AI-assisted with human review of flagged cases. Recall is measured relative to the relevant candidates in the pooled evaluation set rather than the entire corpus. The results should therefore be interpreted as preliminary evidence for this evaluation setup, not proof of general superiority across legal retrieval tasks.

**Output artifacts**
- `eval/pooled_evaluation/evaluated_retrieval_results.csv`
- `eval/pooled_evaluation/per_query_metrics.csv`
- `eval/pooled_evaluation/retrieval_metrics_summary.csv`