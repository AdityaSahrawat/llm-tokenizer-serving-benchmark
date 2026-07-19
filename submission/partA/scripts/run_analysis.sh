#!/usr/bin/env bash
# run_analysis.sh
# Regenerates all results in submission/partA/results/ from scratch.
# Run from the repository root: bash submission/partA/scripts/run_analysis.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
CORPUS_DIR="$REPO_ROOT/submission/partA/corpus"
RESULTS_DIR="$REPO_ROOT/submission/partA/results"
SCRIPTS_DIR="$REPO_ROOT/submission/partA/scripts"

FERTILITY="$SCRIPTS_DIR/fertility.py"
COMPARE="$SCRIPTS_DIR/compare_metrics.py"
PLOT="$SCRIPTS_DIR/plot_results.py"

mkdir -p "$RESULTS_DIR/plots"

CORPUS_ARGS=(
  "--corpus" "eng=$CORPUS_DIR/eng.txt"
  "--corpus" "hin=$CORPUS_DIR/hin.txt"
  "--corpus" "kan=$CORPUS_DIR/kan.txt"
  "--corpus" "tam=$CORPUS_DIR/tam.txt"
)

echo "============================================================"
echo " Part A — Tokenizer Fertility Analysis"
echo " Corpus : $CORPUS_DIR"
echo " Results: $RESULTS_DIR"
echo "============================================================"

# ──────────────────────────────────────────────────────────────────
# 1. GPT-2 fertility (corrected script)
# ──────────────────────────────────────────────────────────────────
echo ""
echo "[1/5] GPT-2 fertility (corrected — corpus-level ratio, split())"
uv run python "$FERTILITY" \
  "${CORPUS_ARGS[@]}" \
  --tokenizer gpt2 \
  --lowercase true

# ──────────────────────────────────────────────────────────────────
# 2. XLM-RoBERTa fertility → corrected_fertility.csv
# ──────────────────────────────────────────────────────────────────
echo ""
echo "[2/5] XLM-RoBERTa fertility"
uv run python "$FERTILITY" \
  "${CORPUS_ARGS[@]}" \
  --tokenizer hf:xlm-roberta-base \
  --lowercase true

# ──────────────────────────────────────────────────────────────────
# 3. Denominator comparison → denominator_comparison.csv
# ──────────────────────────────────────────────────────────────────
echo ""
echo "[3/5] Denominator comparison (tok/word, tok/char, tok/byte, tok/sent)"
uv run python "$COMPARE" \
  "${CORPUS_ARGS[@]}" \
  --tokenizer hf:xlm-roberta-base \
  --lowercase true \
  --output "$RESULTS_DIR/denominator_comparison.csv"

# ──────────────────────────────────────────────────────────────────
# 4. Lowercase effect (E02 cross-check)
# ──────────────────────────────────────────────────────────────────
echo ""
echo "[4/5] Lowercase effect cross-check (E02)"
echo "--- With --lowercase true ---"
uv run python "$FERTILITY" \
  "${CORPUS_ARGS[@]}" \
  --tokenizer hf:xlm-roberta-base \
  --lowercase true

echo ""
echo "--- With --lowercase false ---"
uv run python "$FERTILITY" \
  "${CORPUS_ARGS[@]}" \
  --tokenizer hf:xlm-roberta-base \
  --lowercase false

# ──────────────────────────────────────────────────────────────────
# 5. Generate Plots
# ──────────────────────────────────────────────────────────────────
echo ""
echo "[5/5] Generating bar charts in $RESULTS_DIR/plots/"
uv run python "$PLOT"

echo ""
echo "============================================================"
echo " Done. Results written to $RESULTS_DIR"
echo "============================================================"
