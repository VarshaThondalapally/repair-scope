"""Reproduce baseline and both current strategies on the original development set."""
from dataclasses import replace
import hashlib
import html
import json
from pathlib import Path
import statistics
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from benchmarks.baseline_matcher import Matcher as BaselineMatcher, load_synonyms as baseline_aliases
from finding_coder.domains import load_domain,list_domains
from finding_coder.evaluate import evaluate,load_gold
from finding_coder.matcher import Matcher


def run():
    results,parity=[],[]
    for domain in list_domains():
        current=load_domain(domain)
        frozen=load_domain(str(ROOT/"benchmarks/baseline_domains"/domain))
        frozen=replace(frozen,matcher=BaselineMatcher(frozen.catalog,baseline_aliases(frozen.folder/"synonyms.yaml")))
        cases=load_gold(current.folder/"gold.csv")
        for label,pack in [("original",frozen),("corrected_bm25",replace(current,matcher=Matcher(current.catalog,current.matcher.synonyms,strategy="bm25"))),("hybrid",current)]:
            s=evaluate(pack,cases)
            durations=[]
            for case in cases:
                start=time.perf_counter()
                ranked=pack.matcher.rank(case.finding)
                durations.append((time.perf_counter()-start)*1000)
                if label!="original":
                    parity.append({"domain":domain,"strategy":pack.matcher.strategy,"finding":case.finding,
                                   "codes":[c.row.code for c in ranked],"scores":[c.score for c in ranked]})
            results.append({"domain":domain,"strategy":label,"cases":len(cases),"top1":s.top1,"top3":s.top3,
                            "clear_suggestions":s.confident,"clear_wrong":s.confident-s.confident_right,
                            "rules_caught":s.rules_caught,"rule_cases":s.rule_cases,
                            "median_ms":round(statistics.median(durations),3)})
    target=ROOT/"reports"
    target.mkdir(exist_ok=True)
    output={"dataset":"Original synthetic development set; not held out","independent_validation":False,
            "current_automatic_exports":0,"results":results,
            "gold_sha256":{d:hashlib.sha256((ROOT/"domains"/d/"gold.csv").read_bytes()).hexdigest() for d in list_domains()}}
    (target/"benchmark.json").write_text(json.dumps(output,indent=2)+"\n",encoding="utf-8")
    (target/"parity.json").write_text(json.dumps(parity,indent=2)+"\n",encoding="utf-8")
    lines=["# Evaluation","","Reproduce: python tools/benchmark.py","",
           "**All 75 cases are synthetic development data.** The original builder authored the catalogs, rules and expected answers. These cases were inspected during v2 development. They are not held out and do not establish field accuracy.","",
           "| Domain | Engine | First pick | Top three | Clear but wrong | Median latency (ms) |",
           "|---|---|---:|---:|---:|---:|"]
    for r in results:
        lines.append("| {domain} | {strategy} | {top1}/{cases} | {top3}/{cases} | {clear_wrong}/{clear_suggestions} | {median_ms} |".format(**r))
    lines+=["","Clear means a heuristic textual margin, not calibrated confidence. **Every current suggestion requires human approval**, including those with a large margin. No claim about human-reviewed accuracy is made.","",
       "Original code, data and report are preserved under benchmarks/. Its manifest records SHA-256 hashes. Current gold files are unchanged. The RV alias list adds the ordinary faucet/tap equivalence; this is a development change, not independent validation.","",
       "## Compared engines","",
       "- Original: frozen BM25, including the multiword alias flaw.",
       "- Corrected BM25: complete phrase aliases, one alias contribution per group, reduced weight for generic position words.",
       "- Hybrid: corrected BM25 plus adjacent phrases and conservative unknown-word spelling repair. This is lexical retrieval, not embeddings or an LLM.","",
       "## Remaining failures","",
       "Symptoms can resemble several repairs. Shared words do not establish a cause. Negation, multiple issues, abbreviations and missing catalog vocabulary remain limitations. Review prompts do not diagnose repairs or guarantee every ambiguity is caught.","",
       "Companion checks evaluate configured example rules against selected rows. A rule firing does not establish that work was performed, is universally required, or is separately billable. A practitioner must validate rules and hours.","",
       "## Validation still needed","",
       "A practitioner-labeled, de-identified set collected independently of the builder; multiple legitimate labels where appropriate; frozen tuning/test splits; reviewer correction rates and task completion time; missed or inapplicable companion work. Add semantic retrieval only with a measured benefit.","",
       "The public demo runs entirely in the browser. Python/browser retrieval parity is tested on all 75 original findings in both current strategies. Ranked codes must agree; minor floating-point differences are tolerated."]
    report="\n".join(lines)+"\n"
    (ROOT/"docs/EVALUATION.md").write_text(report,encoding="utf-8")
    (ROOT/"web/evaluation.html").write_text('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>RepairScope evaluation</title><link rel="stylesheet" href="styles.css"></head><body><main><p><a href="./">← Back to demo</a></p><section class="panel"><h1>Evaluation & limitations</h1><pre class="evaluation-text">'+html.escape(report)+'</pre></section></main></body></html>',encoding="utf-8")
    print("\n".join(lines[:15]))


if __name__=="__main__":
    run()
