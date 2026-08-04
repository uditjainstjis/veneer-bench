# langchain-ai/openevals — issue draft (awaiting Udit's go)

**Target:** https://github.com/langchain-ai/openevals
**Why this repo:** 1.1k stars, pushed within the last day, only 14 open issues — maintainers
demonstrably read them. Its entire purpose is LLM-as-judge evaluators, so the finding is
directly on-topic rather than adjacent.

**Diligence gate:** repo is live (pushed 2026-08-03), not archived, low issue backlog, no
existing issue or PR on formatting/style bias in prompts (checked). This is a
maintainer-facing observation with a concrete one-line change, not a cosmetic tidy.

---

## Title

Most built-in judge prompts don't guard against presentation bias — measured, and it's ~30
points on near-tied candidates

## Body

`CORRECTNESS_PROMPT` already contains the right instinct:

> Focus on correctness of information rather than style or verbosity

That line is doing real work, and I have numbers for how much. Of the 31 built-in prompts,
only three carry a guard like it — `correctness`, `code_correctness` and
`transcription_accuracy`. The rest, including `helpfulness`, `accuracy`, `groundedness` and
`answer_relevance`, don't mention style or formatting at all.

### What I measured

I built answers by *rendering* a fixed list of atomic factual claims into different
presentations, so two candidates can be made byte-identical in content and differ only in
layout. A checker fails the build if any renderer leaks a content word.

With a generic "which answer is better?" rubric and no formatting guidance (972 pairwise
judgments, 3 judges):

| rendering of identical claims | win rate vs plain prose |
|---|---|
| bullets | 74.4% |
| headings | 67.6% |
| **plain vs byte-identical copy (control)** | **50.0%, ties 85%** |
| emoji bullets | 25.5% |
| padded with neutral filler | 9.3% |

A 65-point swing on identical content. The control is what makes it credible: judges tie
85% of the time on a byte-identical copy and split exactly 50/50 when forced, so this isn't
judge noise — they become decisive only when the clothes change.

### The important caveat, because it bounds the claim

This **does not** survive a real content difference. If the prettier answer is missing even
1 claim out of 6, judges reject it 100% of the time (measured at gaps of 1, 2 and 3 claims,
Gemini 3 Flash).

So this isn't "LLM judges love markdown". It's narrower and, I think, more useful:

> Judge scores are reliable when candidates genuinely differ, and decay toward a formatting
> lottery as candidates approach a tie.

Which is exactly the regime a lot of openevals usage sits in — regression suites where the
new output is *almost* the same as the old one, and A/B comparisons between close models.

### Suggested change

Add the guard you already use in `CORRECTNESS_PROMPT` to the prompts that grade substance.
For example in `helpfulness`:

```diff
 <Instructions>
   - Read the input and output carefully
+  - Judge the substance of the response. Presentation, formatting, layout and length are
+    not quality and should not affect the score
 </Instructions>
```

Happy to open a PR across the substance-grading prompts if you think it's worth doing, and
to leave the style-focused ones (`conciseness`, `agent_tone`, `vocal_affect`) alone since
presentation *is* the thing being graded there.

### Reproduce

Corpus, harness and the substance-invariance checker:
- https://github.com/uditjainstjis/veneer-bench
- https://www.kaggle.com/datasets/uditjain13/veneer-llm-judge-format-bias

Open leaderboard scoring judges on format-neutrality:
- https://www.kaggle.com/benchmarks/uditjain13/veneer-llm-judge-format-bias

---

## Etiquette checklist before posting

- [ ] Authored as Udit, no Claude trailers or attribution
- [ ] No AI-policy violation — openevals has no stated ban (Pallets / libjpeg-turbo do)
- [ ] Issue first, PR only if a maintainer says yes (avoids the B2 blunder: unsolicited
      cosmetic PR on a dormant thread)
- [ ] Numbers re-checked against `release/summary.csv` before posting
