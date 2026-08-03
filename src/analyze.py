"""VENEER analysis: win rates, noise floor, position bias, bootstrap CIs, figures."""
import json, collections, math, random, warnings
warnings.filterwarnings("ignore")
import pandas as pd
import numpy as np

CTRL = "plain_vs_plain"
ORDER = ["plain_vs_plain", "bullets", "numbered", "table", "headers",
         "bold_terms", "emoji", "markdown_max", "padded"]
AXIS = {"plain_vs_plain": "control", "bullets": "structure", "numbered": "structure",
        "headers": "structure", "table": "structure", "bold_terms": "emphasis",
        "markdown_max": "emphasis", "emoji": "emphasis", "padded": "length"}
SHORT = {"claude-opus-5": "Opus 5", "claude-sonnet-5": "Sonnet 5",
         "claude-haiku-4-5-20251001": "Haiku 4.5"}


def load():
    rows = [json.loads(l) for l in open("results/judgments.jsonl") if l.strip()]
    df = pd.DataFrame(rows).drop_duplicates(subset=["id", "rendering", "judge"], keep="last")
    df["judge_s"] = df["judge"].map(lambda x: SHORT.get(x, x))
    return df


def win_rate(sub):
    """Fraction of non-tie decisions won by the variant."""
    d = sub[sub.winner != "tie"]
    return float("nan") if len(d) == 0 else (d.winner == "variant").mean()


def boot(sub, n=4000, seed=11):
    d = (sub[sub.winner != "tie"].winner == "variant").astype(int).values
    if len(d) < 3:
        return (float("nan"), float("nan"))
    rng = np.random.default_rng(seed)
    s = rng.choice(d, size=(n, len(d)), replace=True).mean(axis=1)
    return float(np.percentile(s, 2.5)), float(np.percentile(s, 97.5))


def main():
    df = load()
    print(f"{len(df)} judgments · {df.id.nunique()} items · {df.judge.nunique()} judges\n")

    rec = []
    for r in ORDER:
        sub = df[df.rendering == r]
        if len(sub) == 0:
            continue
        lo, hi = boot(sub)
        rec.append({"rendering": r, "axis": AXIS[r], "n": len(sub),
                    "tie_rate": (sub.winner == "tie").mean(),
                    "win_rate": win_rate(sub), "ci_lo": lo, "ci_hi": hi,
                    **{SHORT[j]: win_rate(sub[sub.judge == j])
                       for j in sub.judge.unique()}})
    tab = pd.DataFrame(rec)
    floor = tab.loc[tab.rendering == CTRL, "win_rate"]
    floor = float(floor.iloc[0]) if len(floor) else 0.5
    fhi = tab.loc[tab.rendering == CTRL, "ci_hi"]
    fhi = float(fhi.iloc[0]) if len(fhi) else 0.5
    # The control ties ~85% of the time, so its non-tie sample is tiny and its CI
    # is uninformative. The correct test for a format effect is therefore whether
    # the variant's own CI excludes indifference (0.50), two-sided.
    tab["deviation_pp"] = ((tab.win_rate - .5) * 100).round(1)
    tab["differs_from_50"] = (tab.ci_lo > .5) | (tab.ci_hi < .5)

    pd.set_option("display.width", 200, "display.max_columns", 30)
    print(tab.round(3).to_string(index=False))
    tab.round(4).to_csv("results/summary.csv", index=False)

    # ---- THE LEADERBOARD METRIC ----------------------------------------
    # VENEER score = mean absolute deviation from 50% win rate across all
    # non-control renderings, in percentage points. It is the amount of a
    # judge's verdict that presentation alone can buy. 0 = format-blind.
    lb = []
    for j in sorted(df.judge_s.unique()):
        sub = df[(df.judge_s == j) & (df.rendering != CTRL)]
        per_r = sub.groupby("rendering").apply(win_rate).dropna()
        ctrl = df[(df.judge_s == j) & (df.rendering == CTRL)]
        dev = (per_r - .5).abs()
        # A judge whose verdict is dominated by WHERE an answer sits produces a
        # win rate pulled toward 0.5 for every condition, which is
        # indistinguishable from genuine format-blindness unless position is
        # reported alongside. So it always is.
        nt = sub[sub.winner != "tie"]
        first_pick = float((nt.raw == "A").mean())
        second = (nt[nt.plain_first].winner == "variant").mean()
        firstpos = (nt[~nt.plain_first].winner == "variant").mean()
        gap = float(second - firstpos)
        lb.append({"judge": j,
                   "VENEER_score": round(float(dev.mean() * 100), 2),
                   # the format that moves this judge furthest from indifference,
                   # in EITHER direction -- not merely the one it likes most
                   "most_moved_by": dev.idxmax(),
                   "its_win_rate": round(float(per_r[dev.idxmax()]), 3),
                   "first_pick_rate": round(first_pick, 3),
                   "position_gap": round(gap, 3),
                   "position_confounded": abs(gap) > .5,
                   "tie_rate": round(float((sub.winner == "tie").mean()), 3),
                   "control_win_rate": round(float(win_rate(ctrl)), 3)})
    lbdf = pd.DataFrame(lb).sort_values("VENEER_score")
    print("\n=== VENEER LEADERBOARD (lower = more format-robust judge) ===")
    print(lbdf.to_string(index=False))
    lbdf.to_csv("results/leaderboard.csv", index=False)

    # position bias: how often the judge picked whichever answer was shown first
    df["picked_first"] = df.raw == "A"
    pb = df[df.winner != "tie"].groupby("judge_s").picked_first.mean()
    print("\nPosition bias (P[picks the answer shown first], 0.5 = unbiased):")
    print(pb.round(3).to_string())

    # per-domain, maximal formatting only
    mm = df[df.rendering == "markdown_max"]
    if len(mm):
        print("\nmarkdown_max win rate by domain:")
        print(mm.groupby("domain").apply(win_rate).round(3).to_string())

    with open("results/headline.json", "w") as f:
        best = tab[tab.rendering != CTRL].sort_values("win_rate", ascending=False)
        json.dump({
            "n_judgments": int(len(df)), "n_items": int(df.id.nunique()),
            "judges": sorted(df.judge_s.unique().tolist()),
            "noise_floor_win_rate": round(floor, 4),
            "noise_floor_ci_hi": round(fhi, 4),
            "top_rendering": best.iloc[0]["rendering"],
            "top_win_rate": round(float(best.iloc[0]["win_rate"]), 4),
            "top_ci": [round(float(best.iloc[0]["ci_lo"]), 4),
                       round(float(best.iloc[0]["ci_hi"]), 4)],
            "bottom_rendering": best.iloc[-1]["rendering"],
            "bottom_win_rate": round(float(best.iloc[-1]["win_rate"]), 4),
            "swing_pp": round(float(best.iloc[0]["win_rate"]
                                    - best.iloc[-1]["win_rate"]) * 100, 1),
            "control_tie_rate": round(float(
                tab.loc[tab.rendering == CTRL, "tie_rate"].iloc[0]), 4),
            "variant_tie_rate": round(float(
                tab[tab.rendering != CTRL]["tie_rate"].mean()), 4),
            "n_significant": int(tab[tab.rendering != CTRL]["differs_from_50"].sum()),
            "control_tie_by_judge": {
                j: round(float((df[(df.judge_s == j) & (df.rendering == CTRL)].winner
                                == "tie").mean()), 3)
                for j in sorted(df.judge_s.unique())},
            "position_bias": {j: round(float(
                (df[(df.winner != "tie") & (df.judge_s == j)].raw == "A").mean()), 3)
                for j in sorted(df.judge_s.unique())},
            "per_judge_top": {c: round(float(best.iloc[0][c]), 4)
                              for c in SHORT.values() if c in best.columns},
            "leaderboard": lbdf.to_dict("records"),
        }, f, indent=1)
    print("\nwrote results/summary.csv + results/headline.json")

    figures(df, tab, floor)


def figures(df, tab, floor):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    COL = {"control": "#8a8a8a", "structure": "#3b7dd8", "emphasis": "#d9534f",
           "length": "#e0a800"}
    t = tab.sort_values("win_rate")
    fig, ax = plt.subplots(figsize=(9, 5.2))
    ax.barh(t.rendering, t.win_rate, color=[COL[a] for a in t.axis], height=.68)
    ax.errorbar(t.win_rate, range(len(t)),
                xerr=[t.win_rate - t.ci_lo, t.ci_hi - t.win_rate],
                fmt="none", ecolor="#222", elinewidth=1.1, capsize=3)
    ax.axvline(.5, color="#222", lw=1, ls="--")
    ax.axvline(floor, color="#8a8a8a", lw=1.4, ls=":")
    ax.set_xlabel("win rate vs. identical-content plain prose (ties excluded)")
    ax.set_title("VENEER: how far presentation alone moves an LLM judge",
                 fontsize=13, weight="bold")
    ax.text(floor, -.9, " noise floor", color="#555", fontsize=8, va="top")
    ax.set_xlim(0, 1)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    handles = [plt.Rectangle((0, 0), 1, 1, color=COL[a]) for a in COL]
    ax.legend(handles, list(COL), title="axis", frameon=False, loc="lower right")
    fig.tight_layout()
    fig.savefig("figures/win_rates.png", dpi=170)

    piv = (df[df.winner != "tie"].assign(w=lambda d: d.winner == "variant")
           .pivot_table(index="rendering", columns="judge_s", values="w"))
    piv = piv.reindex([r for r in ORDER if r in piv.index])
    fig, ax = plt.subplots(figsize=(7.2, 5))
    im = ax.imshow(piv.values, cmap="RdBu_r", vmin=.2, vmax=.8, aspect="auto")
    ax.set_xticks(range(len(piv.columns)), piv.columns)
    ax.set_yticks(range(len(piv.index)), piv.index)
    for i in range(piv.shape[0]):
        for j in range(piv.shape[1]):
            v = piv.values[i, j]
            if not math.isnan(v):
                ax.text(j, i, f"{v:.2f}", ha="center", va="center", fontsize=9,
                        color="white" if abs(v - .5) > .18 else "#111")
    ax.set_title("Format-bias win rate by judge", fontsize=12, weight="bold")
    fig.colorbar(im, ax=ax, shrink=.8, label="win rate vs plain")
    fig.tight_layout()
    fig.savefig("figures/by_judge.png", dpi=170)
    print("wrote figures/win_rates.png + figures/by_judge.png")


if __name__ == "__main__":
    main()
