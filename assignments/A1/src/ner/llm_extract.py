r"""
OPTIONAL local-LLM structured extraction (brief §15) — evaluated, not assumed.

Runs a small local model through Ollama's HTTP API with a strict JSON schema and
a system prompt that FORBIDS invention. Its only purpose here is to be measured
against the NER and hybrid pipelines on the same 206-phrase gold set, so the
decision to use it (or not) rests on evidence rather than on the assumption that
"an LLM must be better".

Usage:  python src/ner/llm_extract.py [model] [--limit N]
"""
from __future__ import annotations
import json, sys, time, pathlib, urllib.request, hashlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
CACHE = ROOT / "data/interim/llm_cache"; CACHE.mkdir(parents=True, exist_ok=True)
URL = "http://127.0.0.1:11434/api/generate"

SYSTEM = """You extract structured data from a single recipe ingredient phrase.

RULES - these are absolute:
- Return ONLY information that is literally present in the phrase.
- If a field is not stated, its value MUST be null (or [] for list fields).
- NEVER guess, infer, complete or normalise a quantity, unit, temperature, time
  or state that the phrase does not state.
- "ingredient_surface" is the ingredient NAME exactly as written, with no
  quantity, no unit, no preparation words, and no container words.
- If the phrase names several distinct ingredients, list them all.

Reply with ONE JSON object and nothing else:
{"ingredients":[{"ingredient_surface":str,"quantity":str|null,"unit":str|null,
"processing_state":[str],"quality_state":[str],"temperature":str|null,"time":str|null}]}"""


def ask(model: str, phrase: str, timeout: int = 120) -> dict | None:
    key = hashlib.sha1(f"{model}|{phrase}".encode()).hexdigest()[:20]
    cp = CACHE / f"{key}.json"
    if cp.exists():                                    # batching + caching (§52)
        return json.loads(cp.read_text())
    body = json.dumps({
        "model": model,
        "prompt": f"{SYSTEM}\n\nIngredient phrase:\n{phrase}\n\nJSON:",
        "stream": False, "format": "json",
        "options": {"temperature": 0, "seed": 20260908, "num_predict": 320},
    }).encode()
    req = urllib.request.Request(URL, data=body, headers={"Content-Type": "application/json"})
    try:
        raw = json.loads(urllib.request.urlopen(req, timeout=timeout).read())
        out = json.loads(raw.get("response", "{}"))
    except Exception as e:
        out = {"_error": repr(e)[:160]}
    cp.write_text(json.dumps(out))
    return out


def extract(model: str):
    def f(phrase: str) -> list[str]:
        d = ask(model, phrase) or {}
        if "_error" in d:
            return []
        items = d.get("ingredients") or []
        if isinstance(items, dict):
            items = [items]
        out = []
        for it in items:
            if isinstance(it, dict):
                v = it.get("ingredient_surface")
                if isinstance(v, str) and v.strip():
                    out.append(v.strip())
            elif isinstance(it, str) and it.strip():
                out.append(it.strip())
        return out
    return f


def main() -> int:
    model = sys.argv[1] if len(sys.argv) > 1 else "qwen2.5:3b"
    gold = [json.loads(l) for l in (ROOT / "data/interim/gold_eval.jsonl").open()]
    lim = None
    if "--limit" in sys.argv:
        lim = int(sys.argv[sys.argv.index("--limit") + 1])
        gold = gold[:lim]
    fn = extract(model)
    t0, invalid = time.time(), 0
    for i, r in enumerate(gold, 1):
        out = fn(r["text"])
        if not out:
            invalid += 1
        if i % 25 == 0:
            print(f"  {i}/{len(gold)}  {(time.time()-t0)/i:.2f}s/phrase", flush=True)
    dt = time.time() - t0
    print(f"[llm] model={model} phrases={len(gold)} elapsed={dt:.1f}s "
          f"({dt/len(gold):.2f}s/phrase) empty_or_invalid={invalid} "
          f"({100*invalid/len(gold):.1f}%)")
    (ROOT / "outputs/extensions/llm_runtime.json").write_text(json.dumps({
        "model": model, "n_phrases": len(gold), "seconds_total": round(dt, 1),
        "seconds_per_phrase": round(dt / len(gold), 3),
        "empty_or_invalid_output_rate": round(invalid / len(gold), 4)}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
