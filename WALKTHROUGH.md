# Walkthrough

RepairScope helps a reviewer select rows from a fixed list. It never establishes which repairs are necessary.

## Example 1: a clear component finding

Select the RV sample catalog and enter: Roof vent lid cracked; replacement required.

The matcher ranks catalog rows. The vent-lid row receives points for matching component words. Its code is copied from the catalog exactly. The reviewer selects it, checks the actual repair scope, enters a name, and confirms the review. Approving the finding stores a snapshot of the note, selected row, reviewer, time, and catalog ID. Only then does it enter the CSV draft.

Change the finding after approval: the selection and approval clear. The prior decision cannot silently be reused for a new note.

## Example 2: an uncertain symptom and companion work

Enter: Water collecting beneath the kitchen sink. Source not confirmed.

Several catalog lines may be textually related. The UI asks about evidence and negative statements. It does not establish whether the faucet, fitting, pump, or something else failed. Gather the missing evidence and update the note before choosing work. The product deliberately leaves this decision to a person.

For a companion example, enter: Replace confirmed failed LP regulator. Select RVS-0202. An invented example rule asks for RVS-0201. The reviewer may select the companion after checking it applies, or document an intentionally incomplete draft with an explanation of at least ten characters. A rule is not proof that work occurred or that it can be billed.

## Follow the data

| File | Responsibility |
|---|---|
| finding_coder/catalog.py | Parse CSV; reject duplicates, missing fields, bad hours, malformed records and oversized catalogs |
| finding_coder/matcher.py | Score words, full aliases, and optional spelling suggestions |
| finding_coder/policy.py | Produce review prompts without making a diagnosis |
| finding_coder/rules.py | Evaluate configured when/require relationships |
| finding_coder/checker.py | Validate exact codes and sections |
| finding_coder/export.py | Produce formula-safe CSV cells |
| finding_coder/review.py | Queue every batch finding for review |
| finding_coder/server.py | Optional local API; explicit export attestation and limits |
| web/engine.js | Browser matching, exact-code checks, rule evaluation and approval snapshots |
| web/app.js | The interactive, in-memory review workflow |
| tools/build_web.py | Export Python-loaded data and build the static page |
| tools/benchmark.py | Compare original and current engines on unchanged development cases |

## Why phrase matching matters

An alias group can contain blower and air mover. In the original implementation, expanding blower searched separately for air and mover, giving unrelated air-filter rows points. The current engine looks for air mover as a contiguous normalized phrase. It takes only the best alias contribution from each group.

Spelling suggestions apply only to unknown words of at least five characters. A sufficiently distinct nearest vocabulary word receives reduced weight, and the correction is shown. This can still be wrong. It never authorizes a line.

## A custom domain

A folder contains catalog.csv and may contain synonyms.yaml and rules.yaml. An alias file has a groups list of string lists. A rule has name, reason, when, and require. Conditions support code, section, description_any, and description_none. All configured fields must hold; description phrases use the same normalization as retrieval. The existing domain files are concrete examples.

Loading a Python domain rejects rules that cannot match or be satisfied by any catalog row. Browser custom uploads currently import only the catalog; no rules or aliases are inferred.

## Explaining this in an interview

Be able to show how a finding earns points, why those points are not a probability, how the phrase bug caused an error, why all suggestions require approval, and how the frozen comparison exposes remaining misses. Explain that both domains and the evaluation are invented and AI-assisted. Do not describe the project as an integration with any company or a system used by a real dealership.

Before using it in an interview, run the examples, inspect a failure from docs/EVALUATION.md, and make and explain a small change yourself. The implementation cannot substitute for that understanding.

