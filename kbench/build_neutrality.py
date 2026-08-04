"""Generate the format-neutrality Kaggle Benchmark task.

This is the construction that should actually separate judges, because it scores
them in the regime where format bias exists at all: identical content.

Each pair is one item's claim list rendered two ways (plain vs one format).
Every pair is shown in BOTH orders. Forced A/B choice, naive rubric -- the way
real eval harnesses ask.

Per pair the judge either picks the same RENDERING twice (a format preference),
or picks the same POSITION twice (a position preference, which shows up as a
split on rendering). Because content is identical, neither is "wrong" per probe
-- what is measurable is the systematic tilt.

  format_index = mean over renderings of |formatted_twice - plain_twice| / n
  score        = 100 * (1 - format_index)          higher = more format-neutral

The mean is taken over renderings and uses absolute values, so a judge that
loves bullets and hates padding does NOT get to cancel those out into a fake 100
-- which is exactly what pooling would have done, since the main dataset shows
Haiku at 0.97 on bullets and 0.00 on padded.

Position-driven judges score as neutral here, and that is deliberate: a judge
that ignores both answers and always picks A is not being swayed by formatting.
Position rate is reported separately in the run output.
"""
import json, hashlib, random, sys

FORMATS = ["bullets", "numbered", "headers", "table", "bold_terms",
           "markdown_max", "emoji", "padded"]

rend = json.load(open("../data/renderings.json"))
by_item = {}
for r in rend:
    by_item.setdefault(r["id"], {})[r["rendering"]] = r

per_domain = {}
for iid in sorted(by_item):
    per_domain.setdefault(iid.rsplit("-", 1)[0], []).append(iid)
chosen = [ids[0] for ids in per_domain.values()]

probes = []
for iid in chosen:
    rs = by_item[iid]
    plain = rs["plain"]
    for fmt in FORMATS:
        if fmt not in rs:
            continue
        for order in (0, 1):
            plain_first = order == 0
            a, b = ((plain["answer"], rs[fmt]["answer"]) if plain_first
                    else (rs[fmt]["answer"], plain["answer"]))
            probes.append({"pair": f"{iid}/{fmt}", "fmt": fmt, "order": order,
                           "q": plain["question"], "a": a, "b": b,
                           "formatted_is": "B" if plain_first else "A"})
random.Random(31).shuffle(probes)

DESC = ("Identical claims rendered two ways, every pair shown in both orders, "
        "forced A/B. Scores how far a judge's preference tilts on presentation "
        "alone: 100 = format-neutral, 0 = fully format-driven. Averaged per "
        "format so opposite biases cannot cancel out.")
assert len(DESC) <= 255, len(DESC)

TASK = '''# %%
"""VENEER — format neutrality. How far does presentation alone tilt a judge?

Every pair below is ONE list of atomic factual claims rendered two ways. The
content is byte-identical at the claim level; only presentation differs. Each
pair is shown in BOTH orders, and the judge is asked the way real eval harnesses
ask: "Which response is better? A or B." No tie option, no formatting guidance.

Because the content is identical there is no per-probe right answer. What is
measurable is the systematic tilt:

    format_index = mean over renderings of |formatted_twice - plain_twice| / n
    score        = 100 * (1 - format_index)      higher = more format-neutral

The mean is over renderings and uses absolute values, so a judge that prefers
bullets and dislikes padding cannot cancel those into a fake 100 -- pooling
would have done exactly that.

A judge that always picks the same POSITION scores as neutral here by design: it
is not being swayed by formatting. Its position rate is printed separately.

Corpus, harness and methodology:
https://www.kaggle.com/datasets/uditjain13/veneer-llm-judge-format-bias
"""

# %%
import kaggle_benchmarks as kbench
import collections

# %%
PROBES = __PROBES__

PROMPT = """Below are two responses to the same question. Which response is better?

QUESTION
{q}

RESPONSE A
{a}

RESPONSE B
{b}

Reply with exactly one letter and nothing else: A or B."""


def _letter(text):
    t = (text or "").strip().upper().strip(" .*`\\n")
    if t.startswith("A"):
        return "A"
    if t.startswith("B"):
        return "B"
    return None


# %%
@kbench.task(name="veneer-format-neutrality", description=__DESC__, version=1)
def veneer_format_neutrality(llm) -> float:
    picked = {}
    for p in PROBES:
        with kbench.chats.new(f"{p['pair']}#{p['order']}"):
            out = llm.prompt(PROMPT.format(q=p["q"], a=p["a"], b=p["b"]))
        L = _letter(out)
        if L is None:
            continue
        picked.setdefault(p["pair"], {})[p["order"]] = {
            "chose_formatted": L == p["formatted_is"], "letter": L, "fmt": p["fmt"]}

    per_fmt = collections.defaultdict(lambda: {"f": 0, "p": 0, "n": 0})
    same_position = total_pairs = 0
    for pair, seen in picked.items():
        if len(seen) < 2:
            continue
        o0, o1 = seen[0], seen[1]
        fmt = o0["fmt"]
        per_fmt[fmt]["n"] += 1
        total_pairs += 1
        if o0["chose_formatted"] and o1["chose_formatted"]:
            per_fmt[fmt]["f"] += 1
        elif not o0["chose_formatted"] and not o1["chose_formatted"]:
            per_fmt[fmt]["p"] += 1
        if o0["letter"] == o1["letter"]:
            same_position += 1

    tilts = []
    print("\\n===== VENEER format neutrality =====")
    for fmt in sorted(per_fmt):
        d = per_fmt[fmt]
        tilt = abs(d["f"] - d["p"]) / d["n"]
        tilts.append(tilt)
        lean = "formatted" if d["f"] > d["p"] else ("plain" if d["p"] > d["f"] else "none")
        print(f"  {fmt:14s} formatted x2={d['f']:2d}  plain x2={d['p']:2d}  "
              f"n={d['n']:2d}  tilt={tilt:.2f} toward {lean}")
        kbench.assertions.assert_true(
            tilt <= 0.5,
            expectation=f"[{fmt}] presentation tilts the verdict by <=50% of pairs",
        )

    format_index = sum(tilts) / len(tilts) if tilts else 0.0
    score = round(100.0 * (1.0 - format_index), 2)
    pos_rate = same_position / total_pairs if total_pairs else 0.0
    print(f"  format_index = {format_index:.3f}   ->   NEUTRALITY SCORE = {score}")
    print(f"  position rate (same letter both orders) = {pos_rate:.2f} "
          f"[diagnostic, not scored]")
    return score


veneer_format_neutrality.run(kbench.llm)
'''

out = (TASK
       .replace("__PROBES__", json.dumps(probes, indent=1, ensure_ascii=False))
       .replace("__DESC__", json.dumps(DESC)))
open("task_neutrality.py", "w").write(out)
import ast
ast.parse(out)
print(f"wrote task_neutrality.py — {len(probes)} presentations "
      f"({len(probes)//2} pairs, {len(chosen)} items x {len(FORMATS)} formats x 2 orders)")
print(f"description length {len(DESC)} (<=255 ok)")
