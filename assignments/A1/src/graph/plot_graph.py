r"""
Readable views of the connection graph.

A 30,000-node hairball communicates nothing, so instead of drawing the whole graph
this produces two legible projections:

  1. cuisine_ingredient_map.png  - which ingredients are CHARACTERISTIC of which
     cuisine (ranked by lift = P(ingredient|cuisine)/P(ingredient), so staples like
     olive oil do not dominate every cuisine)
  2. ingredient_state_tree.png   - states drawn as CHILDREN of their parent
     ingredient, coloured by taxonomy category
"""
from __future__ import annotations
import csv, sys, pathlib, collections
import networkx as nx
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = pathlib.Path(__file__).resolve().parents[2]
G_DIR = ROOT / "outputs/extensions/graph"
BLUE, ORANGE, AQUA, VIOLET = "#2a78d6", "#eb6834", "#1baf7a", "#4a3aa7"
INK, MUTED = "#0b0b0b", "#52514e"
CAT = {"PREPARATION": BLUE, "COOKING": ORANGE, "QUALITY": AQUA, "SIZE": VIOLET}
plt.rcParams.update({"figure.dpi": 150, "savefig.dpi": 300, "savefig.bbox": "tight",
                     "figure.facecolor": "white", "axes.facecolor": "white"})


def cuisine_map(n_cuisines=12, per_cuisine=6):
    """
    Deterministic RADIAL SMALL-MULTIPLES layout, one star per cuisine.

    A force-directed layout was tried first and rejected: the cuisines' top
    ingredient sets are almost disjoint, so spring layout just packs a dozen
    disconnected stars into overlapping balls with illegible labels. Fixed polar
    placement round a grid of centres is reproducible and readable, which matters
    more here than looking organic.
    """
    import math
    rows = list(csv.DictReader((G_DIR / "cuisine_ingredient_projection.csv").open(encoding="utf-8")))
    by = collections.defaultdict(list)
    for r in rows:
        by[r["cuisine"]].append(r)
    order = sorted(by, key=lambda c: -int(by[c][0]["n_cuisine_recipes"]))[:n_cuisines]

    ncol = 4
    nrow = math.ceil(len(order) / ncol)
    fig, ax = plt.subplots(figsize=(4.6 * ncol, 4.3 * nrow))
    R = 1.0
    for i, cu in enumerate(order):
        cx, cy = (i % ncol) * 3.9, -(i // ncol) * 3.2
        top = sorted(by[cu], key=lambda r: -float(r["lift"]))[:per_cuisine]
        n_rec = int(by[cu][0]["n_cuisine_recipes"])
        for j, r in enumerate(top):
            ang = math.pi / 2 - 2 * math.pi * j / len(top)
            x, y = cx + R * math.cos(ang), cy + R * math.sin(ang)
            lift = float(r["lift"])
            ax.plot([cx, x], [y * 0 + cy, y], color=MUTED, alpha=0.35,
                    lw=0.6 + 2.2 * min(lift, 40) / 40, zorder=1,
                    solid_capstyle="round")
            ax.scatter([x], [y], s=90 + 5 * int(r["recipes_with_ingredient"]),
                       color=AQUA, zorder=3, linewidths=0, alpha=0.92)
            ha = "left" if math.cos(ang) > 0.1 else ("right" if math.cos(ang) < -0.1 else "center")
            off = 0.16 if ha == "left" else (-0.16 if ha == "right" else 0)
            ax.text(x + off, y + (0.20 if abs(math.cos(ang)) <= 0.1 and math.sin(ang) > 0
                                  else (-0.24 if abs(math.cos(ang)) <= 0.1 else 0)),
                    f"{r['ingredient']}\n×{lift:.0f}", ha=ha, va="center",
                    fontsize=7.6, color=INK, zorder=4)
        ax.scatter([cx], [cy], s=1700, color=ORANGE, zorder=5, linewidths=0, alpha=0.95)
        # long cuisine names must not spill outside the node
        lbl = cu if len(cu) <= 11 else cu.replace(" ", "\n")
        fs = 9.5 if len(max(lbl.split("\n"), key=len)) <= 9 else 7.6
        ax.text(cx, cy + (0.10 if "\n" in lbl else 0.06), lbl, ha="center", va="center",
                fontsize=fs, fontweight="bold", color="white", zorder=6, linespacing=0.95)
        ax.text(cx, cy - (0.22 if "\n" in lbl else 0.16), f"N={n_rec}", ha="center",
                va="center", fontsize=7.2, color="white", zorder=6)
    ax.set_aspect("equal"); ax.axis("off")
    ax.set_title("Extension — cuisine ↔ characteristic-ingredient connection map\n"
                 f"top {n_cuisines} cuisines (N ≥ 30) with their {per_cuisine} most "
                 "CHARACTERISTIC ingredients\n"
                 "×N = lift = P(ingredient | cuisine) ÷ P(ingredient overall), so "
                 "corpus staples like olive oil never dominate",
                 fontsize=13, color=INK, pad=18)
    h = [plt.Line2D([], [], marker="o", ls="", ms=14, color=ORANGE, label="cuisine"),
         plt.Line2D([], [], marker="o", ls="", ms=8, color=AQUA,
                    label="characteristic ingredient (size ∝ recipes)"),
         plt.Line2D([], [], color=MUTED, lw=2.4, alpha=.5, label="edge width ∝ lift")]
    ax.legend(handles=h, loc="lower center", ncol=3, frameon=False, fontsize=9,
              bbox_to_anchor=(0.5, -0.04))
    fig.tight_layout()
    fig.savefig(G_DIR / "cuisine_ingredient_map.png"); plt.close(fig)
    print("[plot] cuisine_ingredient_map.png")


def state_tree(ings=("onion", "potato", "chicken breast", "carrot"), top_states=9):
    nodes = list(csv.DictReader((G_DIR / "nodes.csv").open(encoding="utf-8")))
    edges = list(csv.DictReader((G_DIR / "edges.csv").open(encoding="utf-8")))
    w = {(e["source"], e["target"]): int(e["weight"])
         for e in edges if e["edge_type"] == "HAS_STATE"}
    meta = {n["node_id"]: n for n in nodes if n["node_type"] == "state"}

    fig, axes = plt.subplots(2, 2, figsize=(15, 11))
    for ax, ing in zip(axes.ravel(), ings):
        src = f"ingredient:{ing}"
        kids = sorted(((t, c) for (s, t), c in w.items() if s == src),
                      key=lambda x: -x[1])[:top_states]
        T = nx.Graph(); T.add_node(src)
        for t, c in kids:
            T.add_node(t); T.add_edge(src, t, weight=c)
        pos = nx.spring_layout(T, k=1.4, iterations=260, seed=7)
        pos[src] = [0, 0]
        mx = max([c for _, c in kids], default=1)
        nx.draw_networkx_edges(T, pos, ax=ax, edge_color=MUTED, alpha=0.35,
                               width=[0.5 + 3.0 * T[a][b]["weight"] / mx for a, b in T.edges()])
        nx.draw_networkx_nodes(T, pos, nodelist=[src], ax=ax, node_size=2100,
                               node_color=INK, linewidths=0)
        nx.draw_networkx_nodes(
            T, pos, nodelist=[t for t, _ in kids], ax=ax,
            node_size=[260 + 900 * c / mx for _, c in kids],
            node_color=[CAT.get(meta[t]["state_category"], MUTED) for t, _ in kids],
            linewidths=0, alpha=0.92)
        nx.draw_networkx_labels(T, pos, {src: ing.replace(" ", "\n")}, ax=ax,
                                font_size=9 if len(ing) > 10 else 11,
                                font_color="white", font_weight="bold")
        nx.draw_networkx_labels(
            T, pos, {t: f"{meta[t]['state_text']}\n{c}" for t, c in kids},
            ax=ax, font_size=7.6, font_color=INK)
        ax.set_title(f"{ing} — observed processed forms", fontsize=11, color=INK)
        ax.axis("off")
    h = [plt.Line2D([], [], marker="o", ls="", ms=11, color=v, label=k) for k, v in CAT.items()]
    fig.legend(handles=h, loc="lower center", ncol=4, frameon=False, bbox_to_anchor=(0.5, 0.005))
    fig.suptitle("Extension — processed states as SUB-PARTS of their parent ingredient\n"
                 "(node size and edge width ∝ number of recipes; the canonical "
                 "ingredient stays the parent node and is never replaced)",
                 fontsize=12.5, color=INK)
    fig.tight_layout(rect=[0, 0.035, 1, 0.96])
    fig.savefig(G_DIR / "ingredient_state_tree.png"); plt.close(fig)
    print("[plot] ingredient_state_tree.png")


if __name__ == "__main__":
    cuisine_map(); state_tree(); sys.exit(0)
