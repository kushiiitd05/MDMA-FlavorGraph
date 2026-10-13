"""
Prepare TASTEset (github.com/taisti/TASTEset, MIT) as per-ingredient-phrase NER
training data in spaCy DocBin format.

TASTEset annotates a whole ingredient *list* with character offsets over the
concatenated block. We split on newlines and remap offsets so that each training
example is a single ingredient phrase - which is exactly the unit our pipeline
sees at inference time (Q1b operates per ingredient phrase).

Tag mapping (TASTEset -> our tag set, following the recipe-NER conventions of
Diwan/Batra/Bagler, arXiv:2402.17447):
    FOOD             -> NAME       (the ingredient name  <- what Q1(b) requires)
    COLOR            -> NAME       (merged: "red" in "red chilli" is part of the
    PART             -> NAME        ingredient identity, as is "breast" in
                                    "chicken breast" - see evaluation round 1)
    QUANTITY         -> QUANTITY
    UNIT             -> UNIT
    PROCESS          -> STATE      (processing/preparation state)
    PHYSICAL_QUALITY -> STATE      (e.g. 'fresh', 'large'  - physical descriptors)
    TASTE/PURPOSE            -> dropped (sparse, not part of ingredient identity)

Adjacent NAME spans separated only by whitespace are MERGED into one span, so
"red"+"chilli" becomes the single entity "red chilli".
"""
from __future__ import annotations
import json, random, pathlib, sys
import pandas as pd, spacy
from spacy.tokens import DocBin

ROOT = pathlib.Path(__file__).resolve().parents[2]
MAP = {"FOOD": "NAME", "COLOR": "NAME", "PART": "NAME",
       "QUANTITY": "QUANTITY", "UNIT": "UNIT",
       "PROCESS": "STATE", "PHYSICAL_QUALITY": "STATE"}


def merge_adjacent(spans, line: str):
    """Join NAME spans that are contiguous in the text (whitespace/hyphen only)."""
    spans = sorted(spans)
    out = []
    for a, b, t in spans:
        if out and t == "NAME" and out[-1][2] == "NAME":
            gap = line[out[-1][1]:a]
            if gap.strip(" -") == "":
                out[-1] = (out[-1][0], b, "NAME")
                continue
        out.append((a, b, t))
    return out


def explode(df: pd.DataFrame) -> list[tuple[str, list[tuple[int, int, str]]]]:
    """Split each ingredient block into lines and remap entity offsets."""
    out = []
    for block, ents_json in zip(df.ingredients, df.ingredients_entities):
        ents = json.loads(ents_json)
        off = 0
        for line in block.split("\n"):
            lo, hi = off, off + len(line)
            keep = []
            for e in ents:
                if e["start"] >= lo and e["end"] <= hi:
                    t = MAP.get(e["type"])
                    if t:
                        keep.append((e["start"] - lo, e["end"] - lo, t))
            line_s = line.strip()
            # merge adjacent NAME spans separated only by whitespace
            keep = merge_adjacent(keep, line)
            if line_s and keep:
                # account for leading whitespace stripped off the line
                pad = len(line) - len(line.lstrip())
                keep = [(a - pad, b - pad, t) for a, b, t in keep if a - pad >= 0]
                keep = [(a, b, t) for a, b, t in keep if b <= len(line_s)]
                if keep:
                    out.append((line_s, sorted(keep)))
            off = hi + 1  # +1 for the newline
    return out


def to_docbin(nlp, rows, path: pathlib.Path) -> int:
    db, kept, dropped = DocBin(), 0, 0
    for text, ents in rows:
        doc = nlp.make_doc(text)
        spans, taken = [], []
        for a, b, lab in ents:
            sp = doc.char_span(a, b, label=lab, alignment_mode="contract")
            if sp is None or any(not (sp.end <= s.start or sp.start >= s.end) for s in taken):
                dropped += 1
                continue
            spans.append(sp); taken.append(sp)
        if spans:
            doc.ents = spans
            db.add(doc); kept += 1
    db.to_disk(path)
    print(f"  {path.name}: {kept} docs (dropped {dropped} misaligned/overlapping spans)")
    return kept


def main() -> int:
    df = pd.read_csv(ROOT / "data/external/TASTEset.csv")
    rows = explode(df)
    print(f"[tasteset] {len(df)} ingredient blocks -> {len(rows)} labelled ingredient phrases")

    rng = random.Random(20260908)
    rng.shuffle(rows)
    n_dev = int(0.15 * len(rows))
    dev, train = rows[:n_dev], rows[n_dev:]

    nlp = spacy.blank("en")
    out = ROOT / "data/interim/ner_corpus"; out.mkdir(parents=True, exist_ok=True)
    to_docbin(nlp, train, out / "train.spacy")
    to_docbin(nlp, dev, out / "dev.spacy")

    import collections
    c = collections.Counter(t for _, es in rows for *_, t in es)
    print("[tasteset] label distribution:", dict(c.most_common()))
    (out / "phrases_all.jsonl").write_text(
        "\n".join(json.dumps({"text": t, "ents": e}) for t, e in rows), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
