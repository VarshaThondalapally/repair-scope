# Evaluation

Reproduce: python tools/benchmark.py

**All 75 cases are synthetic development data.** The original builder authored the catalogs, rules and expected answers. These cases were inspected during v2 development. They are not held out and do not establish field accuracy.

| Domain | Engine | First pick | Top three | Clear but wrong | Median latency (ms) |
|---|---|---:|---:|---:|---:|
| property_restoration | original | 23/38 | 30/38 | 6/24 | 0.419 |
| property_restoration | corrected_bm25 | 24/38 | 31/38 | 6/24 | 0.681 |
| property_restoration | hybrid | 24/38 | 31/38 | 6/24 | 3.815 |
| rv_service | original | 28/37 | 35/37 | 2/24 | 0.426 |
| rv_service | corrected_bm25 | 31/37 | 36/37 | 1/25 | 0.728 |
| rv_service | hybrid | 31/37 | 36/37 | 0/24 | 3.69 |

Clear means a heuristic textual margin, not calibrated confidence. **Every current suggestion requires human approval**, including those with a large margin. No claim about human-reviewed accuracy is made.

Original code, data and report are preserved under benchmarks/. Its manifest records SHA-256 hashes. Current gold files are unchanged. The RV alias list adds the ordinary faucet/tap equivalence; this is a development change, not independent validation.

## Compared engines

- Original: frozen BM25, including the multiword alias flaw.
- Corrected BM25: complete phrase aliases, one alias contribution per group, reduced weight for generic position words.
- Hybrid: corrected BM25 plus adjacent phrases and conservative unknown-word spelling repair. This is lexical retrieval, not embeddings or an LLM.

## Remaining failures

Symptoms can resemble several repairs. Shared words do not establish a cause. Negation, multiple issues, abbreviations and missing catalog vocabulary remain limitations. Review prompts do not diagnose repairs or guarantee every ambiguity is caught.

Companion checks evaluate configured example rules against selected rows. A rule firing does not establish that work was performed, is universally required, or is separately billable. A practitioner must validate rules and hours.

## Validation still needed

A practitioner-labeled, de-identified set collected independently of the builder; multiple legitimate labels where appropriate; frozen tuning/test splits; reviewer correction rates and task completion time; missed or inapplicable companion work. Add semantic retrieval only with a measured benefit.

The public demo runs entirely in the browser. Python/browser retrieval parity is tested on all 75 original findings in both current strategies. Ranked codes must agree; minor floating-point differences are tolerated.
