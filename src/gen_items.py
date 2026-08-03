"""Generate VENEER base items: a question + a fixed set of atomic claims.

The claims are the ONLY substance in the benchmark. Every rendering in
render.py is built from this same list, so any judge-score difference
between renderings is attributable to presentation alone.
"""
import json, subprocess, sys, os, concurrent.futures as cf

DOMAINS = [
    ("science", "natural science (physics, chemistry, biology, earth science)"),
    ("health", "health, medicine and human physiology"),
    ("tech", "software engineering, computing and the internet"),
    ("economics", "economics, finance and markets"),
    ("history", "history and geopolitics"),
    ("everyday", "practical everyday how-to and consumer advice"),
]

PROMPT = """Produce {n} question/answer items about {desc}.

For each item give:
- "question": a real question a person would ask. Open-ended enough that an answer
  has several parts, but with a factually correct answer. No opinion questions.
- "claims": {c} atomic, self-contained, factually TRUE statements. Together they
  form a complete, correct answer to the question. Each claim must be one sentence,
  stand alone without the others, contain no formatting characters (no markdown, no
  bullets, no bold), and no connective words like "first", "also", "finally" that
  imply an ordering.

The claims are the entire substance of the answer. Do not put any of the answer
outside the claims.

Return ONLY a JSON array, no prose, no code fence:
[{{"question": "...", "claims": ["...", "..."]}}]"""


def gen(domain, desc, n, c, model="claude-opus-5"):
    p = PROMPT.format(n=n, desc=desc, c=c)
    try:
        out = subprocess.run(["claude", "-p", p, "--model", model],
                             capture_output=True, text=True, timeout=420).stdout.strip()
    except subprocess.TimeoutExpired:
        return []
    if "```" in out:
        out = out.split("```")[1]
        if out.startswith("json"):
            out = out[4:]
    try:
        items = json.loads(out)
    except Exception:
        s, e = out.find("["), out.rfind("]")
        if s < 0 or e < 0:
            return []
        try:
            items = json.loads(out[s:e + 1])
        except Exception:
            return []
    res = []
    for i, it in enumerate(items):
        q, cl = it.get("question"), it.get("claims")
        if not q or not isinstance(cl, list) or len(cl) < 4:
            continue
        cl = [str(x).strip() for x in cl if str(x).strip()]
        res.append({"id": f"{domain}-{i:02d}", "domain": domain,
                    "question": q.strip(), "claims": cl})
    return res


if __name__ == "__main__":
    per = int(sys.argv[1]) if len(sys.argv) > 1 else 6
    nclaims = 6
    all_items = []
    with cf.ThreadPoolExecutor(max_workers=6) as ex:
        futs = {ex.submit(gen, d, desc, per, nclaims): d for d, desc in DOMAINS}
        for f in cf.as_completed(futs):
            got = f.result()
            print(f"{futs[f]}: {len(got)}", file=sys.stderr)
            all_items += got
    out = os.path.join(os.path.dirname(__file__), "..", "data", "items.json")
    json.dump(all_items, open(out, "w"), indent=1, ensure_ascii=False)
    print(f"wrote {len(all_items)} items -> {out}", file=sys.stderr)
