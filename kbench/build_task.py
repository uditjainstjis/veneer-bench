"""Generate BOTH Kaggle Benchmark task files from the VENEER corpus.

Two tasks over the same underlying items, so the per-model difference between
them is the whole point:

  veneer-format-bias   GUARDED rubric. The judge is told presentation is not
                       quality and is offered EQUIVALENT. Probes: format_only,
                       content_only, trap. Measures "can it ignore formatting
                       when told to".

  veneer-naive-rubric  NAIVE rubric, written the way real eval harnesses write
                       it: "Which response is better? Reply A or B." No tie
                       option, no formatting guidance. Probes: content_only and
                       trap ONLY -- with no EQUIVALENT available, format_only
                       pairs have no correct answer, so they are excluded rather
                       than scored with a made-up criterion. Measures "does it
                       ignore formatting by default".

The headline number is guarded_trap_accuracy - naive_trap_accuracy: how much a
judge loses purely because nobody told it to look past presentation.

Claims are dropped from the MIDDLE of the list, not the tail. Generators tend to
put the least load-bearing claim last, so tail-dropping can produce a "worse"
answer that is barely worse and a trap that is easier than it looks.
"""
import json, hashlib, random, sys

FORMATS = ["bullets", "markdown_max", "padded", "emoji", "headers", "table"]
TRAP_FORMATS = ["markdown_max", "bullets", "emoji"]
DROP = 2

rend = json.load(open("../data/renderings.json"))
items = {i["id"]: i for i in json.load(open("../data/items.json"))}
by_item = {}
for r in rend:
    by_item.setdefault(r["id"], {})[r["rendering"]] = r

sys.path.insert(0, "../src")
import render as R


def seeded(*parts):
    return int(hashlib.sha256("|".join(map(str, parts)).encode()).hexdigest()[:8], 16)


def drop_middle(claims, k=DROP):
    """Remove k claims from the middle, keeping first and last intact."""
    n = len(claims)
    if n <= k + 2:
        return claims[:-k]
    start = (n - k) // 2
    return claims[:start] + claims[start + k:]


per_domain = {}
for iid in sorted(by_item):
    per_domain.setdefault(iid.rsplit("-", 1)[0], []).append(iid)

fmt_probes, truth_probes = [], []
for dom, ids in per_domain.items():
    a_id, b_id = ids[0], ids[1 % len(ids)]

    plain = by_item[a_id]["plain"]
    for fmt in FORMATS:
        h = seeded(a_id, fmt, "fmt")
        pf = h % 2 == 0
        a, b = ((plain["answer"], by_item[a_id][fmt]["answer"]) if pf
                else (by_item[a_id][fmt]["answer"], plain["answer"]))
        fmt_probes.append({"id": f"{a_id}/{fmt}", "kind": "format_only",
                           "q": plain["question"], "a": a, "b": b,
                           "correct": "EQUIVALENT"})

    full = items[b_id]["claims"]
    short = drop_middle(full)
    for fmt in ["plain", "bullets", "headers"]:
        fn = R.RENDERERS[fmt]
        pf = seeded(b_id, fmt, "content") % 2 == 0
        a, b = ((fn(full), fn(short)) if pf else (fn(short), fn(full)))
        truth_probes.append({"id": f"{b_id}/content-{fmt}", "kind": "content_only",
                             "q": items[b_id]["question"], "a": a, "b": b,
                             "correct": "A" if pf else "B"})
    for fmt in TRAP_FORMATS:
        pretty = R.RENDERERS[fmt](short)        # dressed up, missing information
        complete = R.RENDERERS["plain"](full)   # bare, but says everything
        cf = seeded(b_id, fmt, "trap") % 2 == 0
        a, b = ((complete, pretty) if cf else (pretty, complete))
        truth_probes.append({"id": f"{b_id}/trap-{fmt}", "kind": "trap",
                             "q": items[b_id]["question"], "a": a, "b": b,
                             "correct": "A" if cf else "B"})

# Balance the correct answers exactly 50/50 so no constant strategy beats a coin
# flip. Deterministic: walk the probes in id order and flip the pair whenever the
# running counts would otherwise drift.
truth_probes.sort(key=lambda p: p["id"])
counts = {"A": 0, "B": 0}
for p in truth_probes:
    want = "A" if counts["A"] <= counts["B"] else "B"
    if p["correct"] != want:
        p["a"], p["b"] = p["b"], p["a"]
        p["correct"] = want
    counts[want] += 1

guarded = fmt_probes + truth_probes
naive = list(truth_probes)
random.Random(19).shuffle(guarded)
random.Random(23).shuffle(naive)

PARSE = '''
def _verdict(text, allow_tie):
    t = (text or "").strip().upper()
    if allow_tie:
        for tok in ("EQUIVALENT", "EQUAL", "SAME", "TIE"):
            if tok in t:
                return "EQUIVALENT"
    t = t.strip(" .*`\\\\n")
    if t.startswith("A"):
        return "A"
    if t.startswith("B"):
        return "B"
    return "UNPARSED"
'''

GUARDED_PROMPT = '''"""You are evaluating two candidate answers to the same question.

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

Reply with exactly one word and nothing else: A, B, or EQUIVALENT."""'''

NAIVE_PROMPT = '''"""Below are two responses to the same question. Which response is better?

QUESTION
{q}

RESPONSE A
{a}

RESPONSE B
{b}

Reply with exactly one letter and nothing else: A or B."""'''

TEMPLATE = '''# %%
"""__DOC__"""

# %%
import kaggle_benchmarks as kbench

# %%
PROBES = __PROBES__

PROMPT = __PROMPT__

ALLOW_TIE = __ALLOW_TIE__
__PARSE__

# %%
@kbench.task(name="__NAME__", description=__DESC__, version=1)
def __FN__(llm) -> tuple[int, int]:
    passed = 0
    for p in PROBES:
        with kbench.chats.new(p["id"]):
            out = llm.prompt(PROMPT.format(q=p["q"], a=p["a"], b=p["b"]))
        got = _verdict(out, ALLOW_TIE)
        ok = got == p["correct"]
        passed += int(ok)
        kbench.assertions.assert_equal(
            p["correct"], got,
            expectation=f"[{p['kind']}] correct verdict is {p['correct']}",
        )
    return passed, len(PROBES)


__FN__.run(kbench.llm)
'''

GUARDED_DOC = (
    "VENEER (guarded rubric) - can an LLM judge ignore formatting WHEN TOLD TO?\\n\\n"
    "The judge is explicitly told presentation is not quality, and EQUIVALENT is "
    "offered. Probes: format_only (identical claims, presentation differs -> "
    "EQUIVALENT), content_only (same presentation, one side missing claims), and "
    "trap (the PRETTY answer is missing claims, the plain one is complete).\\n\\n"
    "Compare against veneer-naive-rubric, which asks the same underlying question "
    "the way real eval harnesses actually ask it. The gap is the finding.\\n\\n"
    "https://www.kaggle.com/datasets/uditjain13/veneer-llm-judge-format-bias")

NAIVE_DOC = (
    "VENEER (naive rubric) - does an LLM judge ignore formatting BY DEFAULT?\\n\\n"
    "The prompt is written the way real eval harnesses write it: 'Which response "
    "is better? Reply A or B.' No tie option, no guidance about formatting.\\n\\n"
    "Only probes with an unambiguous correct answer are scored: content_only (one "
    "side is missing claims) and trap (the prettily formatted answer is the one "
    "missing claims). Pairs that differ ONLY in formatting have no correct answer "
    "under a forced choice, so they are excluded rather than scored against an "
    "invented criterion.\\n\\n"
    "The per-model difference from veneer-format-bias is how much a judge loses "
    "purely because nobody told it to look past presentation.\\n\\n"
    "https://www.kaggle.com/datasets/uditjain13/veneer-llm-judge-format-bias")

GUARDED_DESC = ('"Two answers built from explicit atomic claims. Some pairs differ only in '
                'formatting (EQUIVALENT is correct), some only in content, and some dress '
                'the WORSE answer in markdown. The judge IS told to ignore presentation."')
NAIVE_DESC = ('"Same answers, but judged the way real eval harnesses ask: Which response '
              'is better? A or B. No tie, no formatting guidance. Scores only pairs with a '
              'real correct answer, including ones where the prettier answer is worse."')


def emit(path, name, fn, doc, desc, probes, prompt, allow_tie):
    s = (TEMPLATE
         .replace("__DOC__", doc)
         .replace("__PROBES__", json.dumps(probes, indent=1, ensure_ascii=False))
         .replace("__PROMPT__", prompt)
         .replace("__ALLOW_TIE__", str(allow_tie))
         .replace("__PARSE__", PARSE)
         .replace("__DESC__", desc)
         .replace("__NAME__", name)
         .replace("__FN__", fn))
    open(path, "w").write(s)
    import ast
    ast.parse(s)
    return len(probes)


n1 = emit("task.py", "veneer-format-bias", "veneer_format_bias",
          GUARDED_DOC, GUARDED_DESC, guarded, GUARDED_PROMPT, True)
n2 = emit("task_naive.py", "veneer-naive-rubric", "veneer_naive_rubric",
          NAIVE_DOC, NAIVE_DESC, naive, NAIVE_PROMPT, False)


def stats(ps):
    k, c = {}, {}
    for p in ps:
        k[p["kind"]] = k.get(p["kind"], 0) + 1
        c[p["correct"]] = c.get(p["correct"], 0) + 1
    return k, c


for label, ps, n in (("guarded", guarded, n1), ("naive", naive, n2)):
    k, c = stats(ps)
    best = max(c.values()) / n
    print(f"{label:8s} {n:3d} probes  kinds={k}  answers={c}  "
          f"best constant strategy = {best:.0%}")
print(f"desc lengths (must be <=255): guarded={len(GUARDED_DESC)-2} naive={len(NAIVE_DESC)-2}")
