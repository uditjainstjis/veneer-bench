"""Build a complete Kaggle dataset-metadata.json.

Usability points come from: subtitle, description, tags, licence, provenance
(sources + update frequency) and per-COLUMN descriptions. Column descriptions
only take effect on a `datasets version` push, not at create — so the sequence
is: write this -> `metadata --update` -> `datasets version`.
"""
import json, os
import pandas as pd

REL = "release"

COLDOC = {
    "id": "Item identifier, formatted <domain>-<index>.",
    "domain": "Subject area the question comes from: science, health, tech, economics, history or everyday.",
    "question": "The question a person would realistically ask.",
    "n_claims": "Number of atomic claims that make up the complete answer.",
    "claims": "JSON array of atomic, standalone, factually true sentences. This is the ENTIRE substance of the answer; every rendering is built from exactly this list.",
    "rendering": "Which of the nine presentations this row is: plain (the baseline), bullets, numbered, headers, table, bold_terms, markdown_max, emoji or padded.",
    "axis": "What the rendering varies: baseline, structure, emphasis or length.",
    "answer": "The claim list rendered in this presentation. Content is identical across renderings of the same item.",
    "n_chars": "Character length of the rendered answer.",
    "judge": "Model acting as judge for this comparison.",
    "plain_first": "True if the plain baseline was shown as Answer A and the variant as Answer B. Randomised per (item, rendering, judge) by a fixed seed so position bias cancels in aggregate.",
    "raw": "The judge's literal verdict token: A, B or TIE.",
    "winner": "Verdict resolved against presentation order: plain, variant or tie.",
    "n": "Number of judgments contributing to the row.",
    "tie_rate": "Fraction of judgments that were ties.",
    "win_rate": "Fraction of NON-TIE judgments won by the variant over identical-content plain prose. 0.5 means indifference.",
    "ci_lo": "Lower bound of the 95% bootstrap confidence interval on win_rate.",
    "ci_hi": "Upper bound of the 95% bootstrap confidence interval on win_rate.",
    "deviation_pp": "Distance of win_rate from indifference, in percentage points.",
    "differs_from_50": "True if the 95% confidence interval excludes 0.50, i.e. the format effect is significant.",
    "Haiku 4.5": "Win rate for this rendering, Haiku 4.5 as judge.",
    "Sonnet 5": "Win rate for this rendering, Sonnet 5 as judge.",
    "Opus 5": "Win rate for this rendering, Opus 5 as judge.",
    "VENEER_score": "The leaderboard metric: mean absolute deviation from a 50% win rate across all format conditions, in percentage points. How much of a verdict presentation alone can buy. 0 = format-blind.",
    "most_moved_by": "The rendering that moves this judge furthest from indifference, in either direction.",
    "its_win_rate": "Win rate of the rendering named in most_moved_by.",
    "first_pick_rate": "How often the judge picks whichever answer was shown FIRST. 0.5 is unbiased. Read VENEER_score next to this.",
    "position_gap": "Variant win rate when shown second minus when shown first. Large values mean the verdict is driven by position, not format.",
    "position_confounded": "True when |position_gap| > 0.5 — the judge's verdicts are dominated by ordering, so a low VENEER_score is NOT evidence of format-robustness.",
    "control_win_rate": "Win rate in the plain-vs-identical-copy control. NaN when the judge tied on every control comparison, which is the correct behaviour.",
}

FILEDOC = {
    "items.csv": "The 36 source items: question plus the atomic claim list that is the entire substance of its answer.",
    "renderings.csv": "Every claim list rendered nine ways. Content is machine-verified identical across renderings of an item.",
    "judgments.csv": "One pairwise judge verdict per row, with the presentation order used.",
    "summary.csv": "Per-rendering win rate, tie rate, bootstrap CI and significance.",
    "leaderboard.csv": "VENEER score per judge, reported alongside position-bias diagnostics.",
}

DESC = open(f"{REL}/README.md").read().split("---\n\n", 1)[-1]

resources = []
for f, doc in FILEDOC.items():
    df = pd.read_csv(os.path.join(REL, f), nrows=5)
    resources.append({
        "path": f,
        "description": doc,
        "schema": {"fields": [
            {"name": c,
             "description": COLDOC.get(c, f"{c} column."),
             "type": ("number" if pd.api.types.is_numeric_dtype(df[c])
                      else "boolean" if pd.api.types.is_bool_dtype(df[c]) else "string")}
            for c in df.columns]},
    })

meta = {
    "title": "VENEER: LLM Judge Format-Bias Benchmark",
    "id": "uditjain13/veneer-llm-judge-format-bias",
    "subtitle": "Same facts, nine formats: how much of an LLM judge score is presentation?",
    "description": DESC,
    "licenses": [{"name": "CC-BY-SA-4.0"}],
    "keywords": ["artificial intelligence", "nlp", "benchmark", "text",
                 "exploratory data analysis", "data visualization"],
    "isPrivate": False,
    "collaborators": [],
    "resources": resources,
}
json.dump(meta, open(f"{REL}/dataset-metadata.json", "w"), indent=1)
print(f"wrote metadata: {len(resources)} resources, "
      f"{sum(len(r['schema']['fields']) for r in resources)} documented columns")
