r"""
Q2 and Q3 — randomised controls of the Assignment-1 cuisine.

Three controls are built, all treating the 11,934-recipe corpus as one cuisine:

  Q2(a)  SIZE-CONTROLLED, BY REPLICA
         For every real recipe of size n, one random recipe of exactly size n is
         built by drawing n distinct ingredients UNIFORMLY from the cuisine's
         ingredient basket. Repeated to give 10 independent random cuisines.
         -> recipe size distribution is preserved exactly, by construction.

  Q2(b)  SIZE-CONTROLLED, BY INVERSE TRANSFORMATION
         Recipe sizes are not copied but SAMPLED from the empirical size
         distribution using inverse-transform sampling:
             draw u ~ U(0,1), return the smallest s with F(s) = P(S <= s) >= u
         Ingredients are then drawn uniformly as above. 10 x the original number
         of recipes (119,340) are generated.
         -> size distribution matches in expectation, with sampling noise.

  Q3     SIZE- AND INGREDIENT-FREQUENCY-CONTROLLED
         Sizes are replicated as in Q2(a), but ingredients are drawn with
         probability PROPORTIONAL TO THEIR FREQUENCY in the original cuisine.
         10 independent random cuisines.
         -> preserves both the size distribution and (closely) the
            frequency-rank distribution.

Sampling method
---------------
Weighted sampling WITHOUT replacement uses the Efraimidis-Spirakis exponential
key: draw E_i ~ Exp(1) independently per item, form k_i = E_i / w_i, and keep the
k items with the SMALLEST keys. This yields successive weighted sampling without
replacement exactly, and vectorises. Uniform sampling is the same routine with
equal weights. Recipes are grouped by size so that `argpartition` can take
exactly the k smallest keys per row.
"""
from __future__ import annotations
import json
import pathlib
import sys
import time
import collections

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from corpus import load_baskets, corpus_stats, SEED  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
DATA.mkdir(exist_ok=True)

N_SETS = 10          # number of independent random cuisines (Q2a, Q3)
INVERSE_MULTIPLIER = 10   # Q2b generates 10x the original recipe count
CHUNK = 4000         # rows per vectorised block


# ------------------------------------------------------------------- sampling
def sample_without_replacement(sizes: np.ndarray, weights: np.ndarray,
                               rng: np.random.Generator) -> list[np.ndarray]:
    """
    For each requested size, draw that many DISTINCT item ids with probability
    proportional to `weights`, without replacement.

    Efraimidis-Spirakis: key_i = Exp(1)_i / w_i ; keep the k smallest keys.
    Recipes are grouped by size so argpartition returns exactly the k smallest.
    """
    n_items = len(weights)
    w = np.asarray(weights, dtype=np.float64)
    w = w / w.sum()
    out: list[np.ndarray | None] = [None] * len(sizes)

    for k in np.unique(sizes):
        rows = np.flatnonzero(sizes == k)
        k = int(k)
        for start in range(0, len(rows), CHUNK):
            block = rows[start:start + CHUNK]
            e = rng.exponential(size=(len(block), n_items))
            keys = e / w                      # broadcast over items
            if k < n_items:
                part = np.argpartition(keys, k - 1, axis=1)[:, :k]
            else:
                part = np.tile(np.arange(n_items), (len(block), 1))
            for r, row_idx in enumerate(block):
                out[row_idx] = np.sort(part[r])
    return out  # type: ignore[return-value]


def inverse_transform_sizes(size_counts: dict[int, int], n_draw: int,
                            rng: np.random.Generator) -> np.ndarray:
    """
    Inverse-transform sampling of recipe sizes from the empirical distribution.

        sizes  s_1 < s_2 < ... < s_m      with probabilities p_j
        CDF    F_j = P(S <= s_j) = sum_{l<=j} p_l
        draw   u ~ U(0,1); return the smallest s_j with F_j >= u
    """
    sizes = np.array(sorted(size_counts), dtype=np.int64)
    counts = np.array([size_counts[int(s)] for s in sizes], dtype=np.float64)
    p = counts / counts.sum()
    cdf = np.cumsum(p)
    cdf[-1] = 1.0                      # guard against floating-point shortfall
    u = rng.random(n_draw)
    return sizes[np.searchsorted(cdf, u, side="left")]


# --------------------------------------------------------------------- driver
def to_name_lists(id_baskets, names) -> list[list[str]]:
    return [[names[i] for i in b] for b in id_baskets]


def size_hist(baskets) -> dict[int, int]:
    return dict(sorted(collections.Counter(len(b) for b in baskets).items()))


def freq_rank(baskets, n_items: int) -> np.ndarray:
    """Ingredient recipe-frequencies, sorted descending (rank order)."""
    c = np.zeros(n_items, dtype=np.int64)
    for b in baskets:
        c[np.asarray(b, dtype=np.int64)] += 1
    return np.sort(c)[::-1]


def main() -> int:
    t_all = time.time()
    print("[controls] loading Assignment-1 corpus")
    baskets_names, names, index = load_baskets()
    st = corpus_stats(baskets_names)
    n_rec, n_items = st["n_recipes"], st["n_unique_ingredients"]
    print(f"      recipes={n_rec:,}  ingredients={n_items:,}")

    real = [np.array(sorted(index[i] for i in b), dtype=np.int64) for b in baskets_names]
    sizes = np.array([len(b) for b in real], dtype=np.int64)
    real_size_hist = size_hist(real)

    # ingredient frequency in the ORIGINAL cuisine -> weights for Q3
    freq = np.zeros(n_items, dtype=np.int64)
    for b in real:
        freq[b] += 1
    uniform_w = np.ones(n_items, dtype=np.float64)

    rng = np.random.default_rng(SEED)
    store: dict = {"seed": SEED, "n_recipes": n_rec, "n_ingredients": n_items,
                   "n_sets": N_SETS, "inverse_multiplier": INVERSE_MULTIPLIER}

    # ---------------------------------------------------------------- Q2(a)
    print(f"[Q2a] size-controlled by replica - {N_SETS} random cuisines "
          f"({N_SETS * n_rec:,} recipes, uniform ingredient draw)")
    t0 = time.time()
    q2a_hists, q2a_fr = [], []
    for s in range(N_SETS):
        bs = sample_without_replacement(sizes, uniform_w, rng)
        q2a_hists.append(size_hist(bs))
        q2a_fr.append(freq_rank(bs, n_items))
        if s == 0:
            np.save(DATA / "Q2a_set01_example.npy",
                    np.array([len(x) for x in bs], dtype=np.int64))
    print(f"      done in {time.time()-t0:.1f}s")

    # ---------------------------------------------------------------- Q2(b)
    n_draw = INVERSE_MULTIPLIER * n_rec
    print(f"[Q2b] size-controlled by inverse transformation - {n_draw:,} recipes")
    t0 = time.time()
    inv_sizes = inverse_transform_sizes(real_size_hist, n_draw, rng)
    q2b = sample_without_replacement(inv_sizes, uniform_w, rng)
    q2b_hist = size_hist(q2b)
    q2b_fr = freq_rank(q2b, n_items)
    print(f"      drawn mean size={inv_sizes.mean():.4f} "
          f"(original {sizes.mean():.4f})  [{time.time()-t0:.1f}s]")

    # ---------------------------------------------------------------- Q3
    print(f"[Q3 ] size + ingredient-frequency controlled - {N_SETS} random cuisines")
    t0 = time.time()
    q3_hists, q3_fr = [], []
    for s in range(N_SETS):
        bs = sample_without_replacement(sizes, freq.astype(np.float64), rng)
        q3_hists.append(size_hist(bs))
        q3_fr.append(freq_rank(bs, n_items))
    print(f"      done in {time.time()-t0:.1f}s")

    # ---------------------------------------------------------------- save
    def pack_hist(h):
        return {str(k): int(v) for k, v in h.items()}

    payload = {
        **store,
        "original": {"size_hist": pack_hist(real_size_hist),
                     "freq_rank": freq_rank(real, n_items).tolist(),
                     "mean_size": float(sizes.mean())},
        "q2a": {"size_hists": [pack_hist(h) for h in q2a_hists],
                "freq_ranks": [f.tolist() for f in q2a_fr]},
        "q2b": {"size_hist": pack_hist(q2b_hist),
                "freq_rank": q2b_fr.tolist(),
                "n_recipes": int(n_draw),
                "mean_size": float(inv_sizes.mean())},
        "q3": {"size_hists": [pack_hist(h) for h in q3_hists],
               "freq_ranks": [f.tolist() for f in q3_fr]},
    }
    out = DATA / "random_controls.json"
    out.write_text(json.dumps(payload))
    print(f"[controls] wrote {out} ({out.stat().st_size/1e6:.1f} MB) "
          f"in {time.time()-t_all:.1f}s total")
    return 0


if __name__ == "__main__":
    sys.exit(main())
