# VENEER — what we actually know

Running record of what has been measured, including the constructions that failed.

## 1. With content held identical, formatting moves the verdict a long way

Main dataset, 972 pairwise judgments, generic rubric ("which answer is better overall?"),
3 Anthropic judges. Same atomic claims, nine renderings:

| rendering | win rate vs identical-content plain prose |
|---|---|
| bullets | 74.4% |
| headers | 67.6% |
| numbered | 67.4% |
| table | 66.0% |
| **plain vs identical copy (control)** | **50.0%, ties 85%** |
| bold_terms | 44.2% (CI contains 50) |
| markdown_max | 34.6% |
| emoji | 25.5% |
| padded | 9.3% |

A 65-point swing on identical content. Control ties 85% of the time and splits exactly
50/50 when forced, so the effect is not judge noise.

## 2. But that bias does NOT survive a real content difference — measured, 2026-08-04

This was tested because the Kaggle benchmark built on traps (a prettily formatted answer
that is *missing claims* vs a plain answer that is complete) failed to separate models.

Gemini 3 Flash, naive rubric ("Which response is better? Reply A or B" — no tie option,
no instruction about formatting), pretty-but-incomplete vs plain-but-complete:

| content gap | pretty-but-worse correctly rejected |
|---|---|
| 1 claim removed of 6 | 12/12 = 100% |
| 2 claims removed of 6 | 12/12 = 100% |
| 3 claims removed of 6 | 12/12 = 100% |

Claims were dropped from the **middle** of the list, not the tail, so the removed content
is load-bearing.

**The hypothesis that removing the "ignore formatting" instruction would collapse
performance is falsified.** It was predicted by both me and the advisor and it is simply
wrong for this model.

### What that means

**Format bias fills a vacuum.** When two candidates genuinely differ in substance — even
by one claim in six — the judge tracks substance and presentation is irrelevant. The
65-point swing in §1 happens precisely because content was held *byte-identical at the
claim level*, leaving the judge no substantive signal to act on.

This is a narrower claim than "LLM judges prefer bullet points", and a more useful one:

> LLM-judge scores are trustworthy when candidates genuinely differ, and degrade toward a
> formatting lottery as candidates approach a tie — which is exactly the regime of
> late-stage preference data and close model-vs-model comparisons.

## 3. Bound, and what has not been tried

**The bound applies to the construction, not the task.** What has been shown is that a
benchmark built on *content-delta traps* does not discriminate between frontier judges —
they all solve it. Three things owed before treating that as a limit:

1. **The construction that produced it:** pretty-but-incomplete vs plain-but-complete,
   content gaps of 1–3 claims, guarded and naive rubrics. Gemini 3 Flash 72/72 and 36/36;
   Gemini 3.1 Flash-Lite 72/72; Claude Haiku 4.5 70/72.
2. **A materially different construction, untried:** score judges in the *identical-content
   regime* instead — forced choice over format_only pairs, each shown in both orders, with
   the task returning a numeric **format-neutrality score** (`100 − 2·|preference − 50|`)
   rather than per-probe pass/fail. The main dataset says this separates models sharply
   (Haiku 28.18 vs Sonnet 8.55 on the VENEER score) where the trap construction does not.
   `kaggle-benchmarks` supports `-> float` return types, so it fits the leaderboard.
3. **What the metric makes free:** the leaderboard renders any numeric return, so nothing
   forces pass/fail probes. And identical-content pairs need no ground-truth labelling at
   all — the correct behaviour is defined by symmetry, which is free to generate at scale.

## 4. Open, honest weaknesses

- Cross-family coverage is thin. gpt-oss-120b, qwen3-next-80b and glm-5 have 429'd on
  every attempt against Kaggle's model proxy.
- The `plain` baseline joins connective-free atomic claims, so it reads as a wall of
  disconnected assertions. A connective-rich prose baseline is the top of the to-do list.
- Everything in §1 is one model family (Anthropic). Everything in §2 is one model.
