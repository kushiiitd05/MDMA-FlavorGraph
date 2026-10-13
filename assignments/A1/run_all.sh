#!/usr/bin/env bash
# Full reproducible pipeline. Stages 2+ rerun from stored data without rescraping.
set -euo pipefail
PY=./.venv/bin/python

train_if_missing () {   # $1 = model dir, $2 = config, $3 = max_epochs, $4 = label
  if [ ! -d "$1/model-best" ]; then
    echo "== training $4 (not found) - deterministic, seed 20260908"
    $PY -m spacy train "$2" --output "$1" \
      --paths.train data/interim/ner_corpus/train.spacy \
      --paths.dev   data/interim/ner_corpus/dev.spacy \
      --training.max_epochs "$3" --system.seed 20260908 2>&1 | tail -6
  fi
}

case "${1:-all}" in
  scrape)   $PY src/scraping/discover_urls.py && $PY src/scraping/scrape.py ;;
  all|*)
    echo "== 1. corpus freeze (validate -> dedup -> stable Recipe IDs)"
    $PY src/parsing/build_corpus.py

    echo "== 2. NER training data (TASTEset -> spaCy DocBin)"
    $PY src/ner/prepare_tasteset.py

    # Model weights are NOT shipped in the submission archive (~1.4 GB); they are
    # retrained here from TASTEset if absent (~10 min total, fully deterministic).
    train_if_missing data/interim/ner_trf config/ner_trf.cfg 12 "transformer NER (distilroberta)"
    train_if_missing data/interim/ner_cnn config/ner_cnn.cfg 60 "CNN NER baseline"

    echo "== 3. Q1b/Q1c  NER extraction + recipe-ingredient table"
    $PY src/ner/extract_ingredients.py
    echo "== 4. NER model selection on the gold set"
    $PY src/ner/evaluate.py
    echo "== 5. Q2 + Q3 analysis and figures"
    $PY src/analysis/analyze.py
    echo "== 6. Q4 nutrition data (USDA FoodData Central)"
    $PY src/analysis/q4_nutrition.py
    echo "== 7. research extensions"
    $PY src/analysis/extensions.py
    $PY src/analysis/process_states.py
    $PY src/graph/build_graph.py
    $PY src/graph/plot_graph.py
    $PY src/instructions/parse_instructions.py
    echo "== 8. package + backup"
    $PY src/validation/package_submission.py
    echo "== 9. validation gate"
    $PY src/validation/validate_all.py
    ;;
esac
