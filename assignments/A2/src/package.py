r"""
Back up the Assignment-2 data and results with checksums.

The assignment states: "You are responsible for backing up the data and results,
which will be used for evaluation."
"""
from __future__ import annotations
import datetime as dt
import gzip
import hashlib
import json
import pathlib
import shutil
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
BK = ROOT / "backup"
BK.mkdir(exist_ok=True)

TARGETS = [
    "outputs/Q1/Q1a_itemsets_size1.csv",
    "outputs/Q1/Q1a_itemsets_size2.csv",
    "outputs/Q1/Q1a_itemsets_size3.csv.gz",
    "outputs/Q1/Q1b_top20_itemsets.csv",
    "outputs/Q1/Q1c_association_rules.csv",
    "outputs/Q1/Q1_summary.json",
    "data/random_controls.json",
]


def sha256(p: pathlib.Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    manifest = {"created": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
                "files": []}
    for rel in TARGETS:
        src = ROOT / rel
        if not src.exists():
            print(f"  WARN missing {rel}")
            continue
        name = src.name.replace(".gz", "")
        dst = BK / f"{name}.{stamp}.gz"
        if src.suffix == ".gz":
            shutil.copy2(src, dst)
        else:
            with src.open("rb") as fi, gzip.open(dst, "wb") as fo:
                shutil.copyfileobj(fi, fo)
        manifest["files"].append({
            "source": rel, "backup": str(dst.relative_to(ROOT)),
            "source_bytes": src.stat().st_size, "source_sha256": sha256(src)})
        print(f"  backed up {rel} -> {dst.name}")

    # keep only the newest archive per logical file
    seen: dict[str, list[pathlib.Path]] = {}
    for p in BK.glob("*.gz"):
        seen.setdefault(p.name.split(".2")[0], []).append(p)
    for group in seen.values():
        for old in sorted(group, key=lambda x: x.stat().st_mtime)[:-1]:
            old.unlink()

    (BK / "MANIFEST.latest.json").write_text(json.dumps(manifest, indent=2))
    print(f"  manifest written ({len(manifest['files'])} files)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
