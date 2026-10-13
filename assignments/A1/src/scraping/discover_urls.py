"""
Q1(a) step 1 - URL discovery.

Builds the recipe-URL universe for BBC Good Food from its XML sitemap index,
then draws a *seeded, reproducible* uniform random sample of candidate URLs.

Sampling policy (see docs/DECISION_LOG.md, D2):
  Uniform random sample WITHOUT replacement over the full recipe-URL universe.
  This preserves the source's natural composition (no artificial cuisine
  balancing) while avoiding the crawl-order bias that a sequential
  sitemap walk would introduce (BBC sitemaps are grouped by publication
  quarter, so a sequential crawl would over-represent recent recipes).
"""
from __future__ import annotations
import re, sys, random, pathlib, urllib.robotparser as urp
import requests, yaml

ROOT = pathlib.Path(__file__).resolve().parents[2]
CFG = yaml.safe_load((ROOT / "config/config.yaml").read_text())


def robots_ok(base: str, ua: str, sample_path: str = "/recipes/") -> bool:
    rp = urp.RobotFileParser()
    rp.set_url(base.rstrip("/") + "/robots.txt")
    rp.read()
    return rp.can_fetch(ua, base.rstrip("/") + sample_path)


def main() -> int:
    s = requests.Session()
    s.headers.update({"User-Agent": CFG["scrape"]["user_agent"]})
    base = CFG["source"]["base_url"]

    if CFG["scrape"]["respect_robots"]:
        allowed = robots_ok(base, CFG["scrape"]["user_agent"])
        print(f"[robots] can_fetch /recipes/ as '*' -> {allowed}")
        if not allowed:
            print("[robots] ABORT: disallowed by robots.txt")
            return 1

    idx = s.get(CFG["source"]["sitemap_index"], timeout=CFG["scrape"]["timeout_s"]).text
    pat = re.compile(CFG["source"]["recipe_sitemap_pattern"])
    submaps = [u for u in re.findall(r"<loc>([^<]+)</loc>", idx) if pat.search(u)]
    print(f"[discover] recipe sub-sitemaps: {len(submaps)}")

    universe: list[str] = []
    for i, m in enumerate(sorted(submaps), 1):
        try:
            t = s.get(m, timeout=CFG["scrape"]["timeout_s"]).text
            locs = re.findall(r"<loc>([^<]+)</loc>", t)
            universe += locs
            print(f"  [{i:>2}/{len(submaps)}] {len(locs):>5} urls  {m.rsplit('/',1)[-1]}")
        except Exception as e:  # keep going; report at the end
            print(f"  [warn] {m}: {e!r}")

    # canonical dedup: strip query/fragment, drop trailing slash
    seen, uni = set(), []
    for u in universe:
        c = u.split("?")[0].split("#")[0].rstrip("/")
        if c not in seen and "/recipes/" in c:
            seen.add(c)
            uni.append(c)
    uni.sort()  # deterministic ordering before sampling
    print(f"[discover] universe (unique, canonical): {len(uni)}")

    rng = random.Random(CFG["project"]["seed"])
    n = min(CFG["scrape"]["sample_size"], len(uni))
    sample = rng.sample(uni, n)
    print(f"[discover] seeded sample: {len(sample)} (seed={CFG['project']['seed']})")

    (ROOT / CFG["paths"]["url_universe"]).write_text("\n".join(uni) + "\n")
    (ROOT / CFG["paths"]["url_sample"]).write_text("\n".join(sample) + "\n")
    print("[discover] wrote", CFG["paths"]["url_universe"], "and", CFG["paths"]["url_sample"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
