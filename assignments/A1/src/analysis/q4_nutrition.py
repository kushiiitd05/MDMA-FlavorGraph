r"""
Q4 - nutritional comparison: boiled egg  vs  boiled rice + daal.

Data source: USDA FoodData Central, SR Legacy (public API, DEMO_KEY).
All values are for the COOKED food, per 100 g edible portion, then combined
into a realistic serving. Nothing is estimated or interpolated: every number
printed comes straight from the API response cached in data/external/usda/.

Comparison bases (both reported, because neither alone is fair):
  (A) per 100 g cooked food
  (B) per realistic serving:
        - boiled egg meal : 2 large eggs = 100 g edible
        - rice + daal meal: 150 g cooked rice + 150 g cooked toor daal
      The serving basis is stated explicitly; it is an assumption, not a fact.
"""
from __future__ import annotations
import json, pathlib, urllib.request, sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
CACHE = ROOT / "data/external/usda"; CACHE.mkdir(parents=True, exist_ok=True)

FOODS = {
    "boiled_egg":   (173424, "Egg, whole, cooked, hard-boiled"),
    "cooked_rice":  (168878, "Rice, white, long-grain, regular, enriched, cooked"),
    "cooked_daal":  (172437, "Pigeon peas (red gram), mature seeds, cooked, boiled, without salt"),
}
NUTRIENTS = [
    ("Energy", "KCAL", "Energy (kcal)"),
    ("Protein", "G", "Protein (g)"),
    ("Total lipid (fat)", "G", "Fat (g)"),
    ("Carbohydrate, by difference", "G", "Carbohydrate (g)"),
    ("Fiber, total dietary", "G", "Dietary fibre (g)"),
    ("Calcium, Ca", "MG", "Calcium (mg)"),
    ("Iron, Fe", "MG", "Iron (mg)"),
    ("Potassium, K", "MG", "Potassium (mg)"),
    ("Zinc, Zn", "MG", "Zinc (mg)"),
    ("Selenium, Se", "UG", "Selenium (ug)"),
    ("Folate, total", "UG", "Folate (ug)"),
    ("Vitamin B-12", "UG", "Vitamin B12 (ug)"),
    ("Vitamin D (D2 + D3)", "UG", "Vitamin D (ug)"),
    ("Choline, total", "MG", "Choline (mg)"),
]


def fetch(fdc_id: int) -> dict:
    p = CACHE / f"{fdc_id}.json"
    if not p.exists():
        url = (f"https://api.nal.usda.gov/fdc/v1/food/{fdc_id}"
               f"?api_key=DEMO_KEY&format=abridged")
        p.write_bytes(urllib.request.urlopen(url, timeout=30).read())
    return json.loads(p.read_text())


def per100(doc: dict) -> dict[str, float | None]:
    out: dict[str, float | None] = {}
    for name, unit, label in NUTRIENTS:
        v = None
        for n in doc.get("foodNutrients", []):
            if n.get("name") == name and (n.get("unitName") or "").upper() == unit:
                v = n.get("amount")
                break
        out[label] = v
    return out


def main() -> int:
    data = {}
    for key, (fid, desc) in FOODS.items():
        doc = fetch(fid)
        data[key] = {"fdc_id": fid, "description": doc.get("description", desc),
                     "data_type": doc.get("dataType"), "per_100g": per100(doc)}
        print(f"[usda] {fid}  {doc.get('description')}")

    # serving basis (stated assumption)
    SERV = {"boiled_egg": 100.0, "cooked_rice": 150.0, "cooked_daal": 150.0}

    def scale(d, g):
        return {k: (None if v is None else round(v * g / 100.0, 2)) for k, v in d.items()}

    egg_serv = scale(data["boiled_egg"]["per_100g"], SERV["boiled_egg"])
    rice_s = scale(data["cooked_rice"]["per_100g"], SERV["cooked_rice"])
    daal_s = scale(data["cooked_daal"]["per_100g"], SERV["cooked_daal"])
    meal_s = {k: (None if rice_s[k] is None or daal_s[k] is None
                  else round(rice_s[k] + daal_s[k], 2)) for k in rice_s}

    rows = []
    for _, _, label in NUTRIENTS:
        rows.append({
            "nutrient": label,
            "egg_per_100g": data["boiled_egg"]["per_100g"][label],
            "rice_per_100g": data["cooked_rice"]["per_100g"][label],
            "daal_per_100g": data["cooked_daal"]["per_100g"][label],
            "serving_2_boiled_eggs_100g": egg_serv[label],
            "serving_rice150g_plus_daal150g": meal_s[label],
        })

    out = {
        "source": "USDA FoodData Central, SR Legacy (public API)",
        "retrieved_via": "https://api.nal.usda.gov/fdc/v1/food/{fdcId}",
        "foods": {k: {"fdc_id": v["fdc_id"], "description": v["description"],
                      "data_type": v["data_type"]} for k, v in data.items()},
        "serving_assumption": {
            "boiled_egg_meal": "2 large eggs = 100 g edible portion",
            "rice_daal_meal": "150 g cooked white rice + 150 g cooked toor (arhar) daal",
            "note": "Serving sizes are a stated assumption, not a measured quantity.",
        },
        "table": rows,
    }
    p = ROOT / "theory/Q4_nutrition_data.json"
    p.write_text(json.dumps(out, indent=2))

    w = 34
    print(f"\n{'nutrient':{w}s} {'egg/100g':>10s} {'rice/100g':>10s} {'daal/100g':>10s} "
          f"| {'2 eggs':>9s} {'rice+daal':>10s}")
    print("-" * (w + 58))
    for r in rows:
        f = lambda x: "  -" if x is None else f"{x:.2f}"
        print(f"{r['nutrient']:{w}s} {f(r['egg_per_100g']):>10s} {f(r['rice_per_100g']):>10s} "
              f"{f(r['daal_per_100g']):>10s} | {f(r['serving_2_boiled_eggs_100g']):>9s} "
              f"{f(r['serving_rice150g_plus_daal150g']):>10s}")
    print(f"\nwrote {p}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
