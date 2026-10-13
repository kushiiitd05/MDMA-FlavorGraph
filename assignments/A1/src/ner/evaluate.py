r"""
Empirical model selection for Q1(b).

Compares candidate ingredient-name extractors on a 206-phrase gold set drawn from
OUR OWN scraped BBC Good Food corpus (150 uniform-random + 56 deliberately hard
phrases: parentheticals, ranges, unicode fractions, alternations, compounds,
quantity-less lines, very long lines).

Two metrics are reported, because they answer different questions:

  1. SURFACE-set  P/R/F1 - did the extractor find the right ingredient strings?
  2. CANONICAL-set P/R/F1 - after normalisation+canonicalisation, did the recipe
     end up with the right ingredient set?  This is the metric that actually
     determines the correctness of Q1(c)/Q2/Q3, so it is the decisive one.

Matching is set-based per phrase; micro-averaged over the gold set.
"""
from __future__ import annotations
import json, os, sys, pathlib, collections
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "normalization"))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from canonicalize import normalize_surface, canonicalize, trim_span, preprocess_phrase  # noqa: E402
import rule_baseline  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[2]


def canon_set(names) -> set[str]:
    out = set()
    for n in names:
        nn, _ = normalize_surface(trim_span(n))
        if nn:
            out.add(canonicalize(nn)[0])
    return out


def surf_set(names) -> set[str]:
    return {" ".join(n.lower().split()) for n in names if n.strip()}


def prf(tp: int, fp: int, fn: int) -> tuple[float, float, float]:
    p = tp / (tp + fp) if tp + fp else 0.0
    r = tp / (tp + fn) if tp + fn else 0.0
    f = 2 * p * r / (p + r) if p + r else 0.0
    return p, r, f


def score(gold_rows, predict, mapper):
    tp = fp = fn = 0
    exact = 0
    errs = []
    for row in gold_rows:
        g = mapper(row["gold_names"])
        p = mapper(predict(row["text"]))
        tp += len(g & p); fp += len(p - g); fn += len(g - p)
        if g == p:
            exact += 1
        elif len(errs) < 400:
            errs.append({"text": row["text"], "gold": sorted(g), "pred": sorted(p),
                         "missed": sorted(g - p), "spurious": sorted(p - g)})
    P, R, F = prf(tp, fp, fn)
    return {"precision": P, "recall": R, "f1": F,
            "exact_set_accuracy": exact / len(gold_rows),
            "tp": tp, "fp": fp, "fn": fn}, errs


# ------------------------------------------------------------------ extractors
def make_ner(model_dir: str):
    import spacy
    nlp = spacy.load(model_dir)

    def f(text: str) -> list[str]:
        return [e.text for e in nlp(preprocess_phrase(text)).ents if e.label_ == "NAME"]
    return f, nlp


def make_hybrid(ner_fn):
    """NER first; deterministic rules only as a FALLBACK when NER returns nothing."""
    def f(text: str) -> list[str]:
        out = ner_fn(text)
        if not out:
            out = rule_baseline.extract(text)
        return out
    return f


def main() -> int:
    gold = [json.loads(l) for l in (ROOT / "data/interim/gold_eval.jsonl").open()]
    print(f"gold phrases: {len(gold)}   gold ingredient mentions: "
          f"{sum(len(r['gold_names']) for r in gold)}\n")

    approaches: dict = {
        "rule_dictionary_baseline": lambda t: rule_baseline.extract(preprocess_phrase(t))}
    md = ROOT / "data/interim/ner_cnn/model-best"
    if md.exists():
        ner_fn, _ = make_ner(str(md))
        approaches["spacy_ner_cnn_tasteset"] = ner_fn
        approaches["hybrid_ner_plus_rules"] = make_hybrid(ner_fn)
    # optional local LLM - included ONLY if an Ollama server is reachable, so the
    # comparison is empirical rather than assumed (brief §14/§15)
    if os.environ.get("EVAL_LLM"):
        try:
            import urllib.request
            urllib.request.urlopen("http://127.0.0.1:11434/api/version", timeout=3)
            import llm_extract
            m = os.environ.get("EVAL_LLM_MODEL", "qwen2.5:3b")
            llm_fn = llm_extract.extract(m)
            approaches[f"local_llm_{m.replace(':','_')}"] = llm_fn
            approaches[f"hybrid_ner_plus_llm_fallback"] = (
                lambda t, a=ner_fn, b=llm_fn: a(preprocess_phrase(t)) or b(t))
            print(f"[eval] local LLM enabled: {m}")
        except Exception as e:
            print(f"[eval] local LLM unavailable, skipping: {e!r}")

    mt = ROOT / "data/interim/ner_trf/model-best"
    if mt.exists():
        trf_fn, _ = make_ner(str(mt))
        approaches["spacy_ner_transformer_tasteset"] = trf_fn
        approaches["hybrid_transformer_plus_rules"] = make_hybrid(trf_fn)

    results, all_errs = {}, {}
    for name, fn in approaches.items():
        s_surf, _ = score(gold, fn, surf_set)
        s_can, errs = score(gold, fn, canon_set)
        results[name] = {"surface": s_surf, "canonical": s_can}
        all_errs[name] = errs

    hdr = f"{'approach':34s} {'surfP':>6s} {'surfR':>6s} {'surfF1':>7s} | {'canP':>6s} {'canR':>6s} {'canF1':>7s} {'exact':>7s}"
    print(hdr); print("-" * len(hdr))
    for n, r in sorted(results.items(), key=lambda kv: -kv[1]["canonical"]["f1"]):
        a, b = r["surface"], r["canonical"]
        print(f"{n:34s} {a['precision']:6.3f} {a['recall']:6.3f} {a['f1']:7.3f} | "
              f"{b['precision']:6.3f} {b['recall']:6.3f} {b['f1']:7.3f} {b['exact_set_accuracy']:7.3f}")

    out = ROOT / "outputs/extensions/ner_evaluation.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"n_gold_phrases": len(gold), "results": results}, indent=2))
    (ROOT / "outputs/extensions/ner_error_analysis.json").write_text(
        json.dumps(all_errs, indent=2, ensure_ascii=False))
    print(f"\nwrote {out} and ner_error_analysis.json")

    best = max(results.items(), key=lambda kv: kv[1]["canonical"]["f1"])[0]
    print(f"\nBEST (canonical F1): {best}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
