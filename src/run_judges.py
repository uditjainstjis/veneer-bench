"""Run the VENEER judge sweep.

Design: pairwise, every rendering against the `plain` baseline of the SAME item,
so the two candidates a judge sees contain identical claims and differ only in
presentation. Presentation order is randomised per (item, rendering, judge) by a
fixed seed, so position bias cancels in aggregate and is separately measurable.

Control condition `plain_vs_plain` pits the baseline against a byte-identical
copy of itself. Its win rate is the judge's noise floor -- any real format effect
has to clear it.

Output is append-only JSONL, so the sweep is resumable.
"""
import json, os, sys, hashlib, subprocess, random, concurrent.futures as cf, threading

JUDGES = ["claude-opus-5", "claude-sonnet-5", "claude-haiku-4-5-20251001"]
OUT = "results/judgments.jsonl"
LOCK = threading.Lock()

TEMPLATE = """You are evaluating two candidate answers to the same question.

QUESTION
{q}

ANSWER A
{a}

ANSWER B
{b}

Which answer is better overall? Judge on accuracy, completeness, clarity and how
useful it would be to the person who asked.

Reply with exactly one token and nothing else: A, B, or TIE."""


def order_seed(item_id, rendering, judge):
    h = hashlib.sha256(f"{item_id}|{rendering}|{judge}|veneer-v1".encode()).hexdigest()
    return int(h[:8], 16)


def parse(out):
    t = out.strip().upper()
    for tok in ("TIE", "A", "B"):
        if t == tok or t.startswith(tok + " ") or t.startswith(tok + "."):
            return tok
    if "TIE" in t:
        return "TIE"
    if t.count("A") and not t.count("B"):
        return "A"
    if t.count("B") and not t.count("A"):
        return "B"
    return None


def judge_one(task):
    item_id, domain, q, rendering, plain_txt, var_txt, judge = task
    seed = order_seed(item_id, rendering, judge)
    plain_first = (seed % 2 == 0)
    a, b = (plain_txt, var_txt) if plain_first else (var_txt, plain_txt)
    prompt = TEMPLATE.format(q=q, a=a, b=b)
    verdict = None
    for _ in range(2):
        try:
            r = subprocess.run(["claude", "-p", prompt, "--model", judge],
                               capture_output=True, text=True, timeout=300)
            verdict = parse(r.stdout)
            if verdict:
                break
        except subprocess.TimeoutExpired:
            pass
    if verdict is None:
        return None
    if verdict == "TIE":
        winner = "tie"
    else:
        chose_first = (verdict == "A")
        winner = "plain" if (chose_first == plain_first) else "variant"
    return {"id": item_id, "domain": domain, "rendering": rendering,
            "judge": judge, "plain_first": plain_first, "raw": verdict,
            "winner": winner}


def main():
    rend = json.load(open("data/renderings.json"))
    by_item = {}
    for r in rend:
        by_item.setdefault(r["id"], {})[r["rendering"]] = r
    done = set()
    if os.path.exists(OUT):
        for line in open(OUT):
            try:
                d = json.loads(line)
                done.add((d["id"], d["rendering"], d["judge"]))
            except Exception:
                pass
    tasks = []
    for item_id, rs in by_item.items():
        plain = rs["plain"]
        for name, row in rs.items():
            variants = [(name, row["answer"])]
            if name == "plain":
                variants = [("plain_vs_plain", plain["answer"])]  # noise-floor control
            for vname, vtxt in variants:
                for j in JUDGES:
                    if (item_id, vname, j) in done:
                        continue
                    tasks.append((item_id, row["domain"], plain["question"],
                                  vname, plain["answer"], vtxt, j))
    random.Random(7).shuffle(tasks)
    print(f"{len(tasks)} judgments to run ({len(done)} cached)", file=sys.stderr)
    n = 0
    fh = open(OUT, "a")
    with cf.ThreadPoolExecutor(max_workers=int(os.environ.get("VENEER_WORKERS", 12))) as ex:
        for res in ex.map(judge_one, tasks):
            n += 1
            if res:
                with LOCK:
                    fh.write(json.dumps(res) + "\n")
                    fh.flush()
            if n % 25 == 0:
                print(f"  {n}/{len(tasks)}", file=sys.stderr, flush=True)
    fh.close()
    print("done", file=sys.stderr)


if __name__ == "__main__":
    main()
