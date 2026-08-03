"""Package VENEER for release: flat data files + dataset cards for HF and Kaggle."""
import json, os, shutil
import pandas as pd

REL = "release"
os.makedirs(REL, exist_ok=True)

items = json.load(open("data/items.json"))
rend = pd.DataFrame(json.load(open("data/renderings.json")))
jud = pd.DataFrame([json.loads(l) for l in open("results/judgments.jsonl") if l.strip()])
head = json.load(open("results/headline.json"))
summ = pd.read_csv("results/summary.csv")
lb = pd.read_csv("results/leaderboard.csv")

pd.DataFrame([{"id": i["id"], "domain": i["domain"], "question": i["question"],
               "n_claims": len(i["claims"]), "claims": json.dumps(i["claims"])}
              for i in items]).to_csv(f"{REL}/items.csv", index=False)
rend.to_csv(f"{REL}/renderings.csv", index=False)
jud.to_csv(f"{REL}/judgments.csv", index=False)
summ.to_csv(f"{REL}/summary.csv", index=False)
lb.to_csv(f"{REL}/leaderboard.csv", index=False)
json.dump(head, open(f"{REL}/headline.json", "w"), indent=1)
for f in ("win_rates.png", "by_judge.png"):
    if os.path.exists(f"figures/{f}"):
        shutil.copy(f"figures/{f}", f"{REL}/{f}")

top = head["top_rendering"]
tw = head["top_win_rate"] * 100
bot = head["bottom_rendering"]
bw = head["bottom_win_rate"] * 100
swing = head["swing_pp"]
ctie = head["control_tie_rate"] * 100
vtie = head["variant_tie_rate"] * 100
floor = head["noise_floor_win_rate"] * 100
best_judge = lb.iloc[0]
worst_judge = lb.iloc[-1]
struct = summ[summ.axis == "structure"].win_rate.mean() * 100
emph = summ[summ.axis == "emphasis"].win_rate.mean() * 100

CARD = f"""# VENEER — a format-bias benchmark for LLM judges

**Same facts. Different clothes. Watch the judge change its mind.**

VENEER measures how much of an LLM judge's verdict is bought by *presentation*
rather than *substance*.

Every answer in this dataset is rendered from one fixed list of atomic claims.
Nine renderers turn that same claim list into plain prose, bullets, a numbered
list, generic markdown headings, a table, bolded key terms, maximal markdown,
emoji bullets, and a padded version. **No renderer adds, removes or alters a
claim** — a machine check in the harness compares the word multiset of every
rendering against its source claims and fails on any leak (it caught a real bug
during construction). So when a judge prefers one rendering over another, that
preference cannot be about content.

## Headline result: a **{swing:.0f}-point swing on identical content**

The same claims win **{tw:.1f}%** of the time dressed as `{top}` and only
**{bw:.1f}%** dressed as `{bot}`. Nothing about the substance changed.

The direction is the interesting part, and it is not "more formatting is better":

- **Structure helps.** Bullets, numbered lists, generic headings and tables
  average **{struct:.1f}%** against plain prose.
- **Decoration hurts.** Bolded terms, emoji bullets and maximal markdown average
  **{emph:.1f}%**. Padding the answer with neutral filler — no new facts — is
  punished hardest.

So an LLM judge is not simply impressed by markdown. It rewards *navigability*
and penalises *ornament and bulk*. Both are pure presentation, and both move the
verdict by more than most real quality differences do.

**The control matters most.** Plain prose judged against a byte-identical copy of
itself ties **{ctie:.0f}%** of the time — the judges correctly see no difference
and decline to choose. Against a reformatted version of the *same claims* the tie
rate collapses to **{vtie:.0f}%**: they become decisive about a difference that
does not exist in the content.

**{head['n_judgments']:,} pairwise judgments** · {head['n_items']} items ·
6 domains · {len(head['judges'])} judges · {head['n_significant']} of 8 format
conditions differ from indifference at 95% confidence.

## The leaderboard metric

**VENEER score** = mean absolute deviation from a 50% win rate across all format
conditions, in percentage points. It is how much of a verdict presentation alone
can buy. **0 = perfectly format-blind.** Lower is better.

| judge | VENEER score ↓ | format that moves it most | its win rate |
|---|---|---|---|
""" + "\n".join(
    f"| {r.judge} | **{r.VENEER_score}** | `{r.most_moved_by}` | {r.its_win_rate*100:.1f}% |"
    for r in lb.itertuples()) + f"""

Most format-robust judge here: **{best_judge.judge}** ({best_judge.VENEER_score}).
Most susceptible: **{worst_judge.judge}** ({worst_judge.VENEER_score}).

## Files

| file | rows | what |
|---|---|---|
| `items.csv` | {len(items)} | question + the atomic claim list that is the entire substance |
| `renderings.csv` | {len(rend)} | every claim list rendered 9 ways |
| `judgments.csv` | {len(jud)} | one pairwise verdict per row, with presentation order |
| `summary.csv` | {len(summ)} | win rate, tie rate and bootstrap CI per rendering |
| `leaderboard.csv` | {len(lb)} | VENEER score per judge |

## Design notes that matter

- **Pairwise, not absolute.** Absolute 1–10 judge scores saturate. Every variant
  is compared against the `plain` rendering of the *same* item.
- **Order is randomised** per (item, rendering, judge) by a fixed seed, so
  position bias cancels in aggregate and is separately reported.
- **The control is the point.** `plain_vs_plain` pits the baseline against a
  byte-identical copy. It ties {ctie:.0f}% of the time, and its forced choices
  split exactly 50/50 — which is what a working judge should do. Because that
  leaves a small non-tie sample, significance is tested against indifference
  (0.50) rather than against the control's own wide interval.
- **Scaffolding is content-free by construction.** Section headings are generic
  ("Overview", "Key Details"), table columns are "Point"/"Detail", padding is
  neutral hedging. None of it carries information.
- **Position bias is real and separately reported.** """ + ", ".join(
    f"{k} picks the first-shown answer {v*100:.0f}% of the time"
    for k, v in head["position_bias"].items()) + """. Randomising presentation
  order per (item, rendering, judge) is therefore load-bearing, not decorative —
  an unrandomised sweep would have measured position, not format.

## Reproduce / extend

```bash
git clone https://github.com/uditjainstjis/veneer-bench && cd veneer-bench
python3 src/render.py data/items.json     # rebuild + verify substance invariance
python3 src/run_judges.py                 # run the sweep (resumable)
python3 src/analyze.py                    # tables, leaderboard, figures
```

Adding a judge is one line in `JUDGES` in `src/run_judges.py`. Adding a format
axis is one pure function in `src/render.py` — if it leaks content, the checker
fails it.

## Why this exists

LLM-as-judge is now load-bearing in RLHF preference data, eval harnesses, agent
self-critique and model-selection decisions. If a judge's verdict moves this far
on presentation alone, then any pipeline that ranks *model outputs* with an LLM
judge is partly ranking *house style* — and models trained on that signal learn
to format, not to be right.

License: CC BY 4.0 (data) / MIT (code). Contributions welcome — especially judges
from other model families.
"""
open(f"{REL}/README.md", "w").write(CARD)

json.dump({
    "title": "VENEER: LLM Judge Format-Bias Benchmark",
    "id": "uditjain13/veneer-llm-judge-format-bias",
    "licenses": [{"name": "CC-BY-4.0"}],
}, open(f"{REL}/dataset-metadata.json", "w"), indent=1)

print(f"release/ built: {len(rend)} renderings, {len(jud)} judgments")
print(f"HEADLINE: {top} wins {tw:.1f}% vs plain (floor {floor:.1f}%)")
