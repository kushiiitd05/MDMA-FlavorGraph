r"""
Shared corpus loader for Assignment 2.

Source of truth: the Assignment-1 deliverable
    A1/outputs/Q1/Q1c_recipe_ingredient.csv   ("Recipe ID", "Ingredient Name")

That file is the (Recipe ID — Ingredient Name) table A1 was graded on. It holds
11,934 recipes over 6,346 unique canonical ingredients — A1 was required to
collect at least 10,000, and delivered 11,934, so the whole corpus is used here
and every count below is reported against N = 11,934.

Membership convention: a recipe is treated as a SET of ingredients (binary
membership, no repeats). The A1 table already satisfies this - verified at load
time - which is the standard basis for item-set mining and for the randomised
controls in Q2/Q3.
"""
from __future__ import annotations
import csv
import pathlib
import collections

ROOT = pathlib.Path(__file__).resolve().parents[1]
A1_TABLE = ROOT.parent / "A1" / "outputs" / "Q1" / "Q1c_recipe_ingredient.csv"

SEED = 20261006  # global RNG seed for every randomised control in this assignment


def load_baskets() -> tuple[list[list[str]], list[str], dict[str, int]]:
    """
    Return (baskets, ingredients, index).

      baskets     list of recipes, each a sorted list of distinct ingredient names
      ingredients the ingredient vocabulary, sorted by descending corpus frequency
                  then alphabetically (deterministic)
      index       ingredient name -> position in `ingredients`
    """
    if not A1_TABLE.exists():
        raise FileNotFoundError(
            f"Assignment-1 table not found at {A1_TABLE}. "
            "Assignment 2 is built directly on the A1 deliverable."
        )

    per_recipe: dict[str, set[str]] = collections.defaultdict(set)
    n_rows = 0
    with A1_TABLE.open(encoding="utf-8") as fh:
        reader = csv.reader(fh)
        header = next(reader)
        if header != ["Recipe ID", "Ingredient Name"]:
            raise ValueError(f"unexpected header in A1 table: {header}")
        for rid, ing in reader:
            n_rows += 1
            per_recipe[rid].add(ing)

    # binary-membership check: the A1 table must contain no repeated pair
    total_memberships = sum(len(s) for s in per_recipe.values())
    if total_memberships != n_rows:
        raise ValueError(
            f"A1 table has {n_rows - total_memberships} duplicate "
            "(recipe, ingredient) rows; membership is not binary."
        )

    baskets = [sorted(per_recipe[r]) for r in sorted(per_recipe)]

    freq = collections.Counter(i for b in baskets for i in b)
    ingredients = sorted(freq, key=lambda x: (-freq[x], x))
    index = {name: k for k, name in enumerate(ingredients)}
    return baskets, ingredients, index


def corpus_stats(baskets: list[list[str]]) -> dict:
    sizes = [len(b) for b in baskets]
    n = len(sizes)
    return {
        "n_recipes": n,
        "n_memberships": sum(sizes),
        "n_unique_ingredients": len({i for b in baskets for i in b}),
        "mean_recipe_size": sum(sizes) / n,
        "min_recipe_size": min(sizes),
        "max_recipe_size": max(sizes),
    }


def size_distribution(baskets) -> dict[int, int]:
    """Recipe-size -> number of recipes."""
    return dict(sorted(collections.Counter(len(b) for b in baskets).items()))


if __name__ == "__main__":
    b, ings, idx = load_baskets()
    st = corpus_stats(b)
    for k, v in st.items():
        print(f"  {k:24s} {v}")
    print(f"  {'most frequent':24s} {ings[:8]}")
