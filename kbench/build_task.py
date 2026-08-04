"""Generate the Kaggle Benchmark task file from the VENEER corpus.

The model under test acts as a JUDGE. Three probe types, deliberately mixed so
no constant answer scores well:

  format_only  identical claims, different presentation  -> EQUIVALENT is correct
  content_only same presentation, one side missing claims -> the fuller side wins
  trap         the PRETTY answer is missing claims, the PLAIN answer is complete
               -> the plain side wins. This is the probe that matters: it asks
               whether presentation can override substance.

A judge that always answers EQUIVALENT scores only the format_only share; one
that always picks a letter fails every format_only probe. Accuracy across the
mix is therefore a real measure of whether a judge can tell a genuine quality
difference from a cosmetic one.
"""
import json, hashlib, random

FORMATS = ["bullets", "markdown_max", "padded", "emoji", "headers", "table"]
DROP = 2  # claims removed to create a genuinely worse answer

rend = json.load(open("../data/renderings.json"))
items = {i["id"]: i for i in json.load(open("../data/items.json"))}
by_item = {}
for r in rend:
    by_item.setdefault(r["id"], {})[r["rendering"]] = r

import sys
sys.path.insert(0, "../src")
import render as R


def seeded(*parts):
    return int(hashlib.sha256("|".join(map(str, parts)).encode()).hexdigest()[:8], 16)


# one item per domain for format probes, a second per domain for content/trap
per_domain = {}
for iid in sorted(by_item):
    per_domain.setdefault(iid.rsplit("-", 1)[0], []).append(iid)

probes = []
for dom, ids in per_domain.items():
    a_id, b_id = ids[0], ids[1 % len(ids)]

    # ---- format_only: identical claims, presentation differs -----------------
    plain = by_item[a_id]["plain"]
    for fmt in FORMATS:
        h = seeded(a_id, fmt, "fmt")
        pf = h % 2 == 0
        a, b = ((plain["answer"], by_item[a_id][fmt]["answer"]) if pf
                else (by_item[a_id][fmt]["answer"], plain["answer"]))
        probes.append({"id": f"{a_id}/{fmt}", "kind": "format_only",
                       "q": plain["question"], "a": a, "b": b, "correct": "EQUIVALENT"})

    # ---- content_only: same presentation both sides, one is missing claims ---
    full = items[b_id]["claims"]
    short = full[:-DROP]
    for fmt in ["plain", "bullets", "headers"]:
        fn = R.RENDERERS[fmt]
        h = seeded(b_id, fmt, "content")
        pf = h % 2 == 0
        a, b = ((fn(full), fn(short)) if pf else (fn(short), fn(full)))
        probes.append({"id": f"{b_id}/content-{fmt}", "kind": "content_only",
                       "q": items[b_id]["question"], "a": a, "b": b,
                       "correct": "A" if pf else "B"})

    # ---- trap: pretty-but-incomplete vs plain-but-complete -------------------
    for fmt in ["markdown_max", "bullets", "emoji"]:
        pretty = R.RENDERERS[fmt](short)     # dressed up, missing information
        complete = R.RENDERERS["plain"](full)  # bare, but says everything
        h = seeded(b_id, fmt, "trap")
        complete_first = h % 2 == 0
        a, b = ((complete, pretty) if complete_first else (pretty, complete))
        probes.append({"id": f"{b_id}/trap-{fmt}", "kind": "trap",
                       "q": items[b_id]["question"], "a": a, "b": b,
                       "correct": "A" if complete_first else "B"})

random.Random(19).shuffle(probes)

TEMPLATE = '''# %%
"""VENEER — can an LLM judge tell a real quality difference from a cosmetic one?

Answers here are built from explicit lists of atomic factual claims, so every
comparison has a defensible ground truth:

  format_only   both sides carry IDENTICAL claims, only presentation differs
                (bullets, headings, a table, emoji, bolding, neutral padding)
                -> correct verdict: EQUIVALENT
  content_only  both sides use the SAME presentation, one is missing claims
                -> correct verdict: the fuller answer
  trap          the prettily formatted answer is MISSING claims; the plain-prose
                answer is complete
                -> correct verdict: the plain answer

The mix is deliberate. Always answering EQUIVALENT only earns the format_only
share; always picking a letter fails every format_only probe. Score is accuracy
across the whole mix.

Corpus, harness and methodology:
https://www.kaggle.com/datasets/uditjain13/veneer-llm-judge-format-bias
"""

# %%
import kaggle_benchmarks as kbench

# %%
PROBES = __PROBES__

PROMPT = """You are evaluating two candidate answers to the same question.

Judge on substance: how much correct, relevant information each answer actually
gives the person who asked. Presentation, formatting, layout, length and style
are not quality.

QUESTION
{q}

ANSWER A
{a}

ANSWER B
{b}

If one answer gives more correct information than the other, reply with that
letter. If both convey the same information, reply EQUIVALENT.

Reply with exactly one word and nothing else: A, B, or EQUIVALENT."""


def _verdict(text):
    t = (text or "").strip().upper()
    for tok in ("EQUIVALENT", "EQUAL", "SAME", "TIE"):
        if tok in t:
            return "EQUIVALENT"
    t = t.strip(" .*`\\n")
    if t.startswith("A"):
        return "A"
    if t.startswith("B"):
        return "B"
    return "UNPARSED"


# %%
@kbench.task(
    name="veneer-format-bias",
    description=(
        "Two answers built from explicit atomic claims. Some pairs differ only in "
        "formatting (EQUIVALENT is correct), some only in content, and some dress "
        "the WORSE answer in markdown. Score = how well a judge separates real "
        "quality from presentation."
    ),
    version=1,
)
def veneer_format_bias(llm) -> tuple[int, int]:
    passed = 0
    for p in PROBES:
        with kbench.chats.new(p["id"]):
            out = llm.prompt(PROMPT.format(q=p["q"], a=p["a"], b=p["b"]))
        got = _verdict(out)
        ok = got == p["correct"]
        passed += int(ok)
        kbench.assertions.assert_equal(
            p["correct"], got,
            expectation=f"[{p['kind']}] correct verdict is {p['correct']}",
        )
    return passed, len(PROBES)


veneer_format_bias.run(kbench.llm)
'''

open("task.py", "w").write(
    TEMPLATE.replace("__PROBES__", json.dumps(probes, indent=1, ensure_ascii=False)))

kinds, correct = {}, {}
for p in probes:
    kinds[p["kind"]] = kinds.get(p["kind"], 0) + 1
    correct[p["correct"]] = correct.get(p["correct"], 0) + 1
n = len(probes)
print(f"wrote task.py — {n} probes")
print("by kind:", kinds)
print("by correct answer:", correct)
print("degenerate-strategy ceilings: "
      f"always-EQUIVALENT {correct.get('EQUIVALENT',0)/n:.0%} · "
      f"always-A {correct.get('A',0)/n:.0%} · always-B {correct.get('B',0)/n:.0%}")
