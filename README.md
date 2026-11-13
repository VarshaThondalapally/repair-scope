# RepairScope

Turn inspection notes into reviewed repair drafts.

An independent work sample for **catalog-grounded, human-reviewed repair-order drafts**.

Built around RV inspection handoffs, with property restoration as a second domain. It is a prototype inspired by a public product workflow, not commissioned by or affiliated with vinny. No OEM code integration, DMS integration, warranty coverage decision, or production deployment is claimed.

## Try it

The dependency-free browser app is in `dist/index.html` after building. Open that file directly, or serve `web/` with any static server. No API key, model download, or backend is needed for the browser demo.

```bash
python -m pip install -r requirements-dev.txt
python tools/benchmark.py
python tools/build_web.py
python -m http.server 8000 --directory web
```

Open http://localhost:8000. Choose **Clear match**, **Unclear symptom**, **Companion work**, or **Spelling variant** to explore. The packaged release also includes Start-Demo.cmd for Windows. The published URL becomes available after the included GitHub Pages workflow succeeds.

## What a user can do

- Record multiple findings against a job or unit reference.
- Rank exact rows from the selected catalog and inspect literal, synonym, and possible spelling matches.
- Compare corrected BM25 with BM25 plus phrase scoring and spelling repair.
- Resolve companion-line warnings or document why an example rule does not apply.
- Select lines manually from the catalog; unknown codes cannot be selected.
- Approve each finding with a reviewer name and explicit confirmation.
- Download approved findings as a formula-safe CSV and a JSON review record.
- Upload a custom CSV catalog. Custom catalogs have no companion rules in the browser UI.

Editing a finding, its selections, or its override invalidates that finding's approval. Changing the unit reference revokes approvals across the draft. Catalog switching asks before clearing the draft. Companion lines are never silently added. A wide score margin never authorizes an export.

## Evidence, not a field-accuracy claim

All bundled catalogs, labor hours, rules, and expected answers are invented. No RV or restoration practitioner has validated them. The original 75 findings were inspected during development, so they are **development/regression data**, not an independent test.

| Domain | Original first pick | Current first pick | Original top three | Current top three |
|---|---:|---:|---:|---:|
| RV service | 28/37 | 31/37 | 35/37 | 36/37 |
| Property restoration | 23/38 | 24/38 | 30/38 | 31/38 |

See [the reproducible comparison](docs/EVALUATION.md), [machine-readable results](reports/benchmark.json), and [the frozen original report](benchmarks/BASELINE_EVAL.md). The original matcher and domain files are retained with SHA-256 hashes. Current gold files are unchanged.

Current automatic exports: **zero**. This is a workflow policy, not evidence that human approval eliminates errors. Restoration still has six wrong top picks among 24 suggestions with a large textual margin; the complete comparison reports this.

## What changed in v2

1. Multiword aliases must match together. For example, an alias from blower to air mover cannot earn points from an unrelated air-filter row.
2. Each alias group contributes once. Related words do not count as several independent evidence sources.
3. Generic direction words receive less weight, and alone cannot produce repair suggestions.
4. Unknown words can receive a lower-weight spelling suggestion. The possible correction is displayed and does not count toward the clear-match heuristic.
5. Symptom-only, negative, and multi-issue notes receive review prompts. These are heuristics, not a diagnostic system.
6. Batch mode queues every finding for a person. The browser requires a separate review confirmation before approval and export.
7. A browser-local workflow adds multiple findings, catalog snapshots, reviewer attestations, and export provenance.

## Architecture

| Area | Implementation |
|---|---|
| Reference retrieval, validation, rules | Python, standard library, PyYAML |
| Optional local JSON API | FastAPI |
| Public browser app | Vanilla JavaScript and CSS; no runtime dependencies |
| Catalogs and examples | CSV and YAML |
| Deployment | Static GitHub Pages via GitHub Actions |
| Verification | pytest, Node test runner, 150 Python/browser ranking comparisons |

`tools/build_web.py` exports validated catalog/rule data to JavaScript and builds a self-contained page. Python and JavaScript retrieval implementations are separate; parity tests catch drift across both strategies and all 75 development findings.

## Test and reproduce

```bash
python tools/benchmark.py
python tools/build_web.py
python -m pytest -q
node --test tests/web-engine.test.mjs tests/draft.test.mjs
```

GitHub Actions on Ubuntu 24.04 passed **101 Python tests, 23 Node tests, and 10 Chromium acceptance tests**. Those browser checks exercised real CSV/JSON downloads, custom uploads, companion-work decisions, approval invalidation, catalog-switch cancellation and phone-width overflow. See [the validation record](docs/VALIDATION.md) and the [public acceptance run](https://github.com/VarshaThondalapally/repair-scope/actions/runs/43527419217). The build passed; public hosting awaits enabling **Settings → Pages → Source → GitHub Actions**. The restricted local Windows environment runs 99 Python tests with two HTTP tests skipped; CI supplies the missing HTTP/browser checks.

For browser acceptance in a development environment with network access: install npm dependencies, run npx playwright install --with-deps chromium, then npm run test:browser. The shipped browser demo itself has no runtime npm dependencies.

```bash
# Optional Python command line
python -m finding_coder match --domain rv_service "roof vent lid cracked"
python -m finding_coder batch --domain rv_service examples/rv_findings.txt --out out
python -m finding_coder serve
```

Batch output has a header-only coded.csv and a review_queue.csv. It does not auto-select billable work. The optional local API requires explicit review confirmation for CSV export. It is intended for localhost development, not an Internet-facing service.

## Bring a catalog

Use `code,section,description,hours` columns. Codes must be unique and nonempty; hours must be finite and nonnegative. Quoted commas, multiline fields, and UTF-8 BOMs are accepted. Browser and Python upload limits are 1 MB and 1,000 rows. Matching never rewrites or invents a code.

For Python, a custom folder can also include rules.yaml and synonyms.yaml. See [the walkthrough](WALKTHROUGH.md). The browser only imports CSV, and explicitly reports that custom completeness rules are absent.

## Privacy and limits

Browser findings and uploads stay in memory in the current tab. There is no analytics, storage, account, backend processing, or shared session. Reloading clears the draft. Only a deliberate export writes your data to a file. The hosted site serves public sample data and static assets.

Review records contain self-reported reviewer names, timestamps, exact row snapshots, and catalog identifiers. They are not authenticated, signed, or tamper-proof. Fingerprints identify snapshots; they do not certify OEM applicability.

This is lexical retrieval, not an LLM or embedding model. It cannot establish root cause, warranty coverage, quantities, prices, manufacturer applicability, or whether companion work is separately billable. Rule checks only evaluate the configured examples; their absence does not establish completeness. Independent practitioner evaluation is the next substantive step.

## Publish

`Publish-GitHub.ps1` checks the authenticated account, builds and tests the project, creates a public repository if needed, pushes without force, enables Pages, and starts the publish workflow. Run it only from a terminal with working GitHub authentication and network access. It reports a deployment link; a started workflow is not a verified live deployment.

GitHub's [custom Pages workflow documentation](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages) describes the hosting setup.

## Authorship

The initial implementation, v2 implementation, tests, documentation, and synthetic data were produced with AI assistance. No independent code review or trade validation is claimed. This repository is intended to make the implementation, decisions, evaluation, and limitations inspectable.

MIT. See [LICENSE](LICENSE).

