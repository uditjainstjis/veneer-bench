# X thread — draft (awaiting Udit's go)

**1/**
Same six facts. One answer written as bullets, one as plain prose. Not a word changed
between them.

An LLM judge picks the bulleted one 74% of the time.

Pad those identical facts with neutral filler instead and it wins 9%.

A 65-point swing on content that is byte-identical.

**2/**
The control is the part that convinced me.

Plain prose judged against a byte-identical copy of itself: ties 85% of the time, and
splits exactly 50/50 when forced to choose.

So the judges aren't noisy. They correctly see no difference when there is none — and turn
decisive the moment only the clothes change.

**3/**
But the bias does NOT survive a real content difference.

Take the prettier answer and remove even 1 claim out of 6, and judges reject it 100% of
the time. Same at 2 and 3 claims.

Format bias fills a vacuum. It appears exactly where candidates are near-tied — which is
late-stage preference data and close model-vs-model comparisons.

**4/**
So I built it as an open benchmark: identical claims, every pair shown in both orders,
forced choice, scored per format so a judge that loves bullets and hates padding can't
cancel those into a fake 100.

Gemini 3.1 Flash-Lite 69.3
Claude Haiku 4.5 57.9
Gemini 3 Flash 54.8

(100 = format-blind)

**5/**
Everything is open — corpus, harness, and the substance-invariance checker that fails the
build if a renderer leaks a single content word.

Benchmark: https://www.kaggle.com/benchmarks/uditjain13/veneer-llm-judge-format-bias
Data: https://www.kaggle.com/datasets/uditjain13/veneer-llm-judge-format-bias
Code: https://github.com/uditjainstjis/veneer-bench

---

## Accuracy check on every number above

| claim | source |
|---|---|
| bullets 74%, padded 9%, 65-pt swing | `release/summary.csv`, 972 judgments, 3 Anthropic judges |
| control ties 85%, splits 50/50 | `results/headline.json` control_tie_rate, noise_floor_win_rate |
| 100% rejection at gaps of 1/2/3 claims | ladder run, Gemini 3 Flash, 12/12 each |
| 69.3 / 57.9 / 54.8 | Kaggle benchmark leaderboard, overall across 2 tasks |

Note the neutrality task numbers alone are 66.67 / 45.83 / 37.50; the figures in post 4 are
the benchmark's **overall** scores across both tasks, which is what the leaderboard shows.
