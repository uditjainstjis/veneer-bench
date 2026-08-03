"""VENEER renderers.

Every renderer is a pure function of the SAME atomic claim list. No renderer
adds, removes or alters a claim. The only things a renderer may introduce are
content-free scaffolding tokens (generic section titles, generic table column
labels, neutral connectives, punctuation, markdown syntax) -- never a fact.

That is what makes the benchmark clean: a judge score difference between two
renderings of the same item cannot be a substance difference, because the
substance is byte-identical at the claim level.
"""
import re

# Content-free scaffolding. Deliberately generic so it carries no information.
HEADERS = ["Overview", "Key Details", "Additional Context", "Further Points",
           "More Information", "Other Considerations"]
TABLE_COLS = ("Point", "Detail")
PAD_LEAD = ["It is worth noting that ", "To put it simply, ", "In practical terms, ",
            "As a general rule, ", "Broadly speaking, ", "Put another way, "]
PAD_TAIL = [" This is a well-established point.", " That detail matters here.",
            " This is generally the case.", " That is the usual situation.",
            " This holds in most circumstances.", " That is worth keeping in mind."]
INTRO = "Here is a summary of the main points relevant to this question."
OUTRO = "Taken together, these points cover the essentials of the question."
EMOJI = ["\U0001F539", "✅", "\U0001F4CC", "\U0001F4A1", "\U0001F50E", "⚡",
         "\U0001F4CA", "\U0001F3AF"]

_NUM = re.compile(r"\b\d[\d,.]*\s*(?:%|[A-Za-z]{1,12})?\b")
_PROPER = re.compile(r"\b(?:[A-Z][a-z]{2,}(?:\s+[A-Z][a-z]{2,})*)\b")


def _bold(claim, limit=2):
    """Wrap up to `limit` key spans in **. Adds markup only -- never words."""
    spans = []
    for m in list(_NUM.finditer(claim))[:limit]:
        spans.append(m.span())
    if len(spans) < limit:
        for m in _PROPER.finditer(claim):
            if m.start() == 0 and not any(c.isdigit() for c in m.group()):
                continue  # skip a plain sentence-initial capital
            spans.append(m.span())
            if len(spans) >= limit:
                break
    if not spans:
        words = sorted(re.finditer(r"\b[a-z]{6,}\b", claim),
                       key=lambda m: -len(m.group()))[:1]
        spans = [m.span() for m in words]
    spans = sorted(set(spans))
    merged, last = [], -1
    for s, e in spans:
        if s >= last:
            merged.append((s, e)); last = e
    out, prev = [], 0
    for s, e in merged:
        out.append(claim[prev:s]); out.append("**" + claim[s:e].rstrip() + "**")
        out.append(claim[e - (len(claim[s:e]) - len(claim[s:e].rstrip())):e][len(claim[s:e].rstrip()):])
        prev = e
    out.append(claim[prev:])
    return "".join(out)


def r_plain(c):
    return " ".join(c)


def r_bullets(c):
    return "\n".join("- " + x for x in c)


def r_numbered(c):
    return "\n".join(f"{i+1}. {x}" for i, x in enumerate(c))


def r_headers(c):
    per, out, h = 2, [], 0
    for i in range(0, len(c), per):
        out.append(f"## {HEADERS[h % len(HEADERS)]}")
        out += ["- " + x for x in c[i:i + per]]
        out.append("")
        h += 1
    return "\n".join(out).strip()


def r_bold_terms(c):
    return " ".join(_bold(x) for x in c)


def r_markdown_max(c):
    """Maximal formatting: structure + emphasis stacked. Still zero duplication --
    an earlier draft appended a summary line that repeated every claim, which the
    substance checker correctly rejected as content duplication."""
    per, out, h = 2, [], 0
    out.append(f"**{INTRO}**")
    out.append("")
    for i in range(0, len(c), per):
        out.append(f"## {HEADERS[h % len(HEADERS)]}")
        out += ["- " + _bold(x) for x in c[i:i + per]]
        out.append("")
        h += 1
    return "\n".join(out).strip()


def r_table(c):
    rows = [f"| {TABLE_COLS[0]} | {TABLE_COLS[1]} |", "| --- | --- |"]
    for i, x in enumerate(c):
        rows.append(f"| {i+1} | {x} |")
    return "\n".join(rows)


def r_padded(c):
    body = []
    for i, x in enumerate(c):
        body.append(PAD_LEAD[i % len(PAD_LEAD)] + x[0].lower() + x[1:]
                    + PAD_TAIL[i % len(PAD_TAIL)])
    return INTRO + " " + " ".join(body) + " " + OUTRO


def r_emoji(c):
    return "\n".join(f"{EMOJI[i % len(EMOJI)]} {x}" for i, x in enumerate(c))


RENDERERS = {
    "plain": r_plain,              # BASELINE
    "bullets": r_bullets,          # structure
    "numbered": r_numbered,        # structure
    "headers": r_headers,          # structure
    "table": r_table,              # structure
    "bold_terms": r_bold_terms,    # emphasis
    "markdown_max": r_markdown_max,  # emphasis (maximal)
    "emoji": r_emoji,              # emphasis
    "padded": r_padded,            # length
}
BASELINE = "plain"
AXIS = {"plain": "baseline", "bullets": "structure", "numbered": "structure",
        "headers": "structure", "table": "structure", "bold_terms": "emphasis",
        "markdown_max": "emphasis", "emoji": "emphasis", "padded": "length"}


def claim_signature(text):
    """Substance fingerprint: the multiset of alphanumeric word tokens.

    Used to assert that a rendering did not add or drop content words beyond
    the whitelisted scaffolding vocabulary.
    """
    return sorted(re.findall(r"[a-z0-9]+", text.lower()))


if __name__ == "__main__":
    import json, sys, collections
    items = json.load(open(sys.argv[1] if len(sys.argv) > 1 else "data/items.json"))
    scaffold = set()
    for s in HEADERS + list(TABLE_COLS) + PAD_LEAD + PAD_TAIL + [INTRO, OUTRO] + ["Summary"]:
        scaffold |= set(re.findall(r"[a-z0-9]+", s.lower()))
    scaffold |= set(str(i) for i in range(1, 60))
    rows, bad = [], 0
    for it in items:
        base = collections.Counter(claim_signature(" ".join(it["claims"])))
        for name, fn in RENDERERS.items():
            txt = fn(it["claims"])
            got = collections.Counter(claim_signature(txt))
            extra = got - base
            missing = base - got
            leak = {w: n for w, n in extra.items() if w not in scaffold}
            if leak or missing:
                bad += 1
                print(f"LEAK {it['id']}/{name}: extra={leak} missing={dict(missing)}",
                      file=sys.stderr)
            rows.append({"id": it["id"], "domain": it["domain"],
                         "question": it["question"], "rendering": name,
                         "axis": AXIS[name], "answer": txt,
                         "n_claims": len(it["claims"]), "n_chars": len(txt)})
    json.dump(rows, open("data/renderings.json", "w"), indent=1, ensure_ascii=False)
    print(f"{len(rows)} renderings from {len(items)} items; substance violations: {bad}",
          file=sys.stderr)
