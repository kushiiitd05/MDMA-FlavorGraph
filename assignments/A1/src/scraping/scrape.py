"""
Q1(a) step 2 - the recipe scraper.

Extraction hierarchy (see docs/DECISION_LOG.md, D3):
    HTTP GET -> HTML -> BeautifulSoup -> schema.org Recipe JSON-LD -> HTML-selector fallback

Design guarantees
-----------------
* RESUMABLE   : visited-URL registry + append-only JSONL; re-running skips done work.
* POLITE      : bounded concurrency, per-worker delay, exponential backoff on 429/5xx.
* LOSSLESS    : the complete raw JSON-LD block is stored verbatim in `raw_jsonld`.
* HONEST      : absent fields are stored as null; nothing is ever fabricated.
* GRACEFUL    : SIGINT flushes the buffer and exits cleanly.
"""
from __future__ import annotations
import json, re, sys, time, signal, random, pathlib, threading, datetime as dt
from concurrent.futures import ThreadPoolExecutor
import requests, yaml
from bs4 import BeautifulSoup

ROOT = pathlib.Path(__file__).resolve().parents[2]
CFG = yaml.safe_load((ROOT / "config/config.yaml").read_text())
SC, PA = CFG["scrape"], CFG["paths"]

_stop = threading.Event()
_lock = threading.Lock()
_buf: list[dict] = []
_fails: list[dict] = []
_stats = {"ok": 0, "fail": 0, "skip": 0}


def _sig(*_):
    print("\n[scrape] SIGINT - finishing in-flight work and flushing...", flush=True)
    _stop.set()


signal.signal(signal.SIGINT, _sig)


# ---------------------------------------------------------------- JSON-LD
def find_recipe_ld(soup: BeautifulSoup) -> tuple[dict | None, object | None]:
    """Return (Recipe node, full JSON-LD document that contained it)."""
    for tag in soup.find_all("script", attrs={"type": "application/ld+json"}):
        txt = tag.string or tag.get_text() or ""
        try:
            doc = json.loads(txt)
        except Exception:
            continue
        stack = [doc]
        while stack:
            node = stack.pop()
            if isinstance(node, dict):
                t = node.get("@type")
                if t == "Recipe" or (isinstance(t, list) and "Recipe" in t):
                    return node, doc
                stack.extend(v for v in node.values() if isinstance(v, (dict, list)))
            elif isinstance(node, list):
                stack.extend(node)
    return None, None


def _txt(v):
    """Coerce a schema.org value to a plain string, or None. Never invents data."""
    if v is None:
        return None
    if isinstance(v, str):
        return v.strip() or None
    if isinstance(v, (int, float)):
        return str(v)
    if isinstance(v, dict):
        return _txt(v.get("name") or v.get("text") or v.get("@id"))
    if isinstance(v, list):
        parts = [p for p in (_txt(x) for x in v) if p]
        return ", ".join(parts) or None
    return None


def flatten_instructions(ri) -> list[str]:
    """Flatten recipeInstructions (str | list[str|HowToStep|HowToSection]) to ordered steps."""
    out: list[str] = []

    def rec(n):
        if n is None:
            return
        if isinstance(n, str):
            s = re.sub(r"\s+", " ", BeautifulSoup(n, "lxml").get_text(" ")).strip()
            if s:
                out.append(s)
        elif isinstance(n, list):
            for x in n:
                rec(x)
        elif isinstance(n, dict):
            t = n.get("@type")
            if t == "HowToSection":
                rec(n.get("itemListElement"))
            else:
                rec(n.get("text") or n.get("name") or n.get("itemListElement"))

    rec(ri)
    return out


# ---------------------------------------------------------------- HTML fallback
def html_fallback(soup: BeautifulSoup) -> dict:
    """Used only when JSON-LD is missing/incomplete. Returns whatever it can find."""
    out: dict = {}
    h1 = soup.find("h1")
    if h1:
        out["title"] = h1.get_text(" ", strip=True)
    ings = [li.get_text(" ", strip=True)
            for li in soup.select('li[class*="ingredient"], ul[class*="ingredient"] li')]
    if ings:
        out["ingredient_phrases_raw"] = ings
    steps = [li.get_text(" ", strip=True)
             for li in soup.select('li[class*="method"] , ol[class*="method"] li, div[class*="method"] li')]
    if steps:
        out["instruction_steps_raw"] = steps
    return out


# ---------------------------------------------------------------- record build
def build_record(url: str, html: str, final_url: str, status: int) -> dict | None:
    soup = BeautifulSoup(html, "lxml")
    rec, doc = find_recipe_ld(soup)

    canon = soup.find("link", rel="canonical")
    canonical_url = (canon.get("href") if canon and canon.get("href") else final_url)
    canonical_url = canonical_url.split("?")[0].split("#")[0].rstrip("/")

    if rec is None:
        fb = html_fallback(soup)
        if not fb.get("ingredient_phrases_raw"):
            return None
        ings, steps = fb["ingredient_phrases_raw"], fb.get("instruction_steps_raw", [])
        title, method = fb.get("title"), "html_fallback"
        rec, doc = {}, None
    else:
        ings = [i.strip() for i in (rec.get("recipeIngredient") or []) if isinstance(i, str) and i.strip()]
        steps = flatten_instructions(rec.get("recipeInstructions"))
        title = _txt(rec.get("name"))
        method = "jsonld"
        if not ings:  # JSON-LD present but ingredient list empty -> try HTML
            fb = html_fallback(soup)
            if fb.get("ingredient_phrases_raw"):
                ings, method = fb["ingredient_phrases_raw"], "jsonld+html_fallback"

    if not ings or not title:
        return None

    nut = rec.get("nutrition") if isinstance(rec.get("nutrition"), dict) else None

    return {
        "source_url": url,
        "canonical_url": canonical_url,
        "source_site": CFG["source"]["site_id"],
        "date_scraped": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "http_status": status,
        "title": title,
        "author": _txt(rec.get("author")),
        "description": _txt(rec.get("description")),
        "ingredient_phrases_raw": ings,
        "instruction_steps_raw": steps,
        "instructions_raw": "\n".join(steps) if steps else None,
        "prep_time_raw": _txt(rec.get("prepTime")),
        "cook_time_raw": _txt(rec.get("cookTime")),
        "total_time_raw": _txt(rec.get("totalTime")),
        "yield_raw": _txt(rec.get("recipeYield")),
        "cuisine_raw": _txt(rec.get("recipeCuisine")),
        "category_raw": _txt(rec.get("recipeCategory")),
        "keywords_raw": _txt(rec.get("keywords")),
        "diet_raw": _txt(rec.get("suitableForDiet")),
        "nutrition_raw": nut,
        "rating_raw": rec.get("aggregateRating") if isinstance(rec.get("aggregateRating"), dict) else None,
        "image_url": _txt(rec.get("image")),
        "date_published_raw": _txt(rec.get("datePublished")),
        "raw_jsonld": doc,
        "n_ingredient_phrases": len(ings),
        "n_instruction_steps": len(steps),
        "extraction_method": method,
        "scrape_status": "ok",
        "scrape_version": CFG["schema"]["scrape_version"],
    }


# ---------------------------------------------------------------- worker
_tl = threading.local()


def session() -> requests.Session:
    if not hasattr(_tl, "s"):
        s = requests.Session()
        s.headers.update({
            "User-Agent": SC["user_agent"],
            "Accept": "text/html,application/xhtml+xml",
            "Accept-Language": "en-GB,en;q=0.9",
        })
        _tl.s = s
    return _tl.s


def fetch_one(url: str) -> None:
    if _stop.is_set():
        return
    s = session()
    last = None
    for attempt in range(SC["max_retries"] + 1):
        if _stop.is_set():
            return
        try:
            r = s.get(url, timeout=SC["timeout_s"])
            if r.status_code == 200:
                rec = build_record(url, r.text, r.url, r.status_code)
                with _lock:
                    if rec:
                        _buf.append(rec)
                        _stats["ok"] += 1
                    else:
                        _fails.append({"url": url, "reason": "no_parsable_recipe", "status": 200})
                        _stats["fail"] += 1
                time.sleep(SC["per_worker_delay_s"] * (0.6 + 0.8 * random.random()))
                return
            if r.status_code in (429, 500, 502, 503, 504):
                last = f"http_{r.status_code}"
                time.sleep(SC["backoff_base_s"] * (2 ** attempt) + random.random())
                continue
            last = f"http_{r.status_code}"
            break  # 404/410 etc: no point retrying
        except Exception as e:
            last = repr(e)[:120]
            time.sleep(SC["backoff_base_s"] * (2 ** attempt) + random.random())
    with _lock:
        _fails.append({"url": url, "reason": last, "status": None})
        _stats["fail"] += 1


# ---------------------------------------------------------------- flush / main
def flush() -> None:
    with _lock:
        if _buf:
            with (ROOT / PA["raw_jsonl"]).open("a", encoding="utf-8") as f:
                for r in _buf:
                    f.write(json.dumps(r, ensure_ascii=False) + "\n")
            with (ROOT / PA["visited"]).open("a", encoding="utf-8") as f:
                for r in _buf:
                    f.write(r["source_url"] + "\n")
            _buf.clear()
        if _fails:
            with (ROOT / PA["failures"]).open("a", encoding="utf-8") as f:
                for r in _fails:
                    f.write(json.dumps(r) + "\n")
            with (ROOT / PA["visited"]).open("a", encoding="utf-8") as f:
                for r in _fails:
                    f.write(r["url"] + "\n")
            _fails.clear()


def main() -> int:
    for p in (PA["raw_jsonl"], PA["visited"], PA["failures"]):
        (ROOT / p).parent.mkdir(parents=True, exist_ok=True)
        (ROOT / p).touch(exist_ok=True)

    urls = [u.strip() for u in (ROOT / PA["url_sample"]).read_text().splitlines() if u.strip()]
    visited = {u.strip() for u in (ROOT / PA["visited"]).read_text().splitlines() if u.strip()}
    todo = [u for u in urls if u not in visited]
    _stats["skip"] = len(urls) - len(todo)
    print(f"[scrape] sample={len(urls)}  already_visited={_stats['skip']}  todo={len(todo)}", flush=True)
    if not todo:
        print("[scrape] nothing to do.")
        return 0

    t0 = time.time()
    done = 0
    with ThreadPoolExecutor(max_workers=SC["max_workers"]) as ex:
        for _ in ex.map(fetch_one, todo):
            done += 1
            if done % SC["checkpoint_every"] == 0:
                flush()
                el = time.time() - t0
                rate = done / el
                print(f"[scrape] {done}/{len(todo)}  ok={_stats['ok']} fail={_stats['fail']}  "
                      f"{rate:.1f} rec/s  eta={(len(todo)-done)/max(rate,1e-9)/60:.1f} min", flush=True)
            if _stop.is_set():
                break
    flush()
    print(f"[scrape] DONE ok={_stats['ok']} fail={_stats['fail']} elapsed={(time.time()-t0)/60:.1f} min")
    return 0


if __name__ == "__main__":
    sys.exit(main())
