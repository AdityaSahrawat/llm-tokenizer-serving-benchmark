# Part A — Tokenizer Audit

## Objective

A previous intern produced tokenizer fertility measurements and submitted conclusions to leadership asserting that Hindi tokenization is approximately 5–6× worse than English when using the GPT-2 tokenizer. Leadership intends to use those measurements for infrastructure capacity planning.

This repository audits whether those measurements, the code that produced them, and the conclusions drawn from them are trustworthy. The audit focuses on reproducibility: every claim made here is backed by an experiment with an exact terminal command, actual output, and a documented conclusion. No result in `analysis.md` or `recommendation.md` is asserted without a corresponding experiment file in `experiments/`.

Part A is divided into four components: corpus construction (`corpus/`), script audit and correction (`scripts/`, `experiments/`), corrected analysis (`analysis.md`), and an executive recommendation (`recommendation.md`).

---

## Repository Organisation

```
partA/
│
├── README.md               ← This file. Navigation and reproduction guide.
├── analysis.md             ← Technical report: A2 audit findings and A3 corrected analysis.
├── recommendation.md       ← Executive memo: one-page production recommendation.
│
├── corpus/
│   ├── README.md           ← Corpus source, languages, size, preprocessing, and limitations.
│   ├── eng.txt             ← English parallel sentences (998 lines).
│   ├── hin.txt             ← Hindi parallel sentences (998 lines).
│   ├── kan.txt             ← Kannada parallel sentences (998 lines).
│   └── tam.txt             ← Tamil parallel sentences (998 lines).
│
├── scripts/
│   ├── fertility.py        ← Corrected fertility benchmark script.
│   ├── compare_metrics.py  ← Denominator comparison script (tok/word, tok/byte, tok/sent).
│   └── run_analysis.sh     ← Shell script to regenerate all results end-to-end.
│
├── experiments/
│   ├── E01_tokenizer_choice.md
│   ├── E02_lowercase_effect.md
│   ├── E03_split_bug.md
│   ├── E04_average_ratio_bug.md
│   ├── E05_parallel_corpus_issue.md
│   └── E06_denominator_comparison.md
│
└── results/
    ├── tokenizer_comparison.csv
    ├── denominator_comparison.csv
    ├── corrected_fertility.csv
    └── plots/
        ├── tokenizer_bar.png
        └── denominator_bar.png
```

### `corpus/`

Contains the multilingual parallel evaluation corpus used throughout the audit. Four languages — English, Hindi, Kannada, Tamil — with 998 parallel sentences each, drawn from the FLORES-200 devtest split. See `corpus/README.md` for source, preprocessing steps, and limitations.

### `scripts/`

Contains all executable scripts required to reproduce the audit from scratch. `fertility.py` is the corrected version of the intern's script. `compare_metrics.py` computes all three fertility denominators. `run_analysis.sh` chains every command in reproducible order.

### `experiments/`

Contains one Markdown file per experiment. Every file follows the same structure: evidence claim, question, hypothesis, method, command, output, observation, and conclusion. The `analysis.md` report references these files directly rather than repeating their content.

### `results/`

Contains only generated artifacts: CSV tables and PNG plots produced by running the scripts. No Markdown. No manual edits. Every file here must be regeneratable by running `run_analysis.sh`.

### `analysis.md`

The technical report. Answers A2 (script audit) and A3 (corrected analysis). References experiment files for evidence rather than reproducing their content inline.

### `recommendation.md`

The executive memo. Addresses a non-technical audience. Maximum one page. States one production recommendation backed by headline numbers.

---

## Experiment Index

| Experiment | Purpose |
|---|---|
| E01 | Compare GPT-2 and XLM-R tokenizers on all four languages |
| E02 | Measure the effect of lowercasing on fertility scores |
| E03 | Identify and fix the whitespace split bug (`split(" ")` vs `split()`) |
| E04 | Identify and fix the averaging bug (per-line mean vs corpus-level ratio) |
| E05 | Evaluate whether a 10-sentence sample corpus is appropriate for this analysis |
| E06 | Compare all three fertility denominators: tok/word, tok/byte, tok/sent |

---

## Reproducing the Audit

All commands are run from the **repository root** (`llm-tokenizer-serving-benchmark/`).

**Step 1 — Run the full pipeline automatically:**

```bash
bash submission/partA/scripts/run_analysis.sh
```

**Step 2 — Or run individual scripts manually:**

```bash
# GPT-2 tokenizer
uv run python submission/partA/scripts/fertility.py \
  --corpus eng=submission/partA/corpus/eng.txt \
  --corpus hin=submission/partA/corpus/hin.txt \
  --corpus kan=submission/partA/corpus/kan.txt \
  --corpus tam=submission/partA/corpus/tam.txt \
  --tokenizer gpt2

# XLM-RoBERTa tokenizer
uv run python submission/partA/scripts/fertility.py \
  --corpus eng=submission/partA/corpus/eng.txt \
  --corpus hin=submission/partA/corpus/hin.txt \
  --corpus kan=submission/partA/corpus/kan.txt \
  --corpus tam=submission/partA/corpus/tam.txt \
  --tokenizer hf:xlm-roberta-base

# Denominator comparison
uv run python submission/partA/scripts/compare_metrics.py \
  --corpus eng=submission/partA/corpus/eng.txt \
  --corpus hin=submission/partA/corpus/hin.txt \
  --corpus kan=submission/partA/corpus/kan.txt \
  --corpus tam=submission/partA/corpus/tam.txt \
  --tokenizer hf:xlm-roberta-base
```

All outputs are written to `submission/partA/results/`.

---

## Outputs

| File | Description |
|---|---|
| `results/corrected_fertility.csv` | Corrected tok/word fertility for all four languages under both tokenizers |
| `results/tokenizer_comparison.csv` | Side-by-side GPT-2 vs XLM-R fertility scores |
| `results/denominator_comparison.csv` | tok/word, tok/byte, and tok/sent for all four languages |
| `results/plots/tokenizer_bar.png` | Bar chart comparing tokenizer fertility across languages |
| `results/plots/denominator_bar.png` | Bar chart comparing denominator choices across languages |

---

## Recommended Reading Order

1. **`corpus/README.md`** — Understand what data was used and its limitations before reading any numbers.
2. **`experiments/E01` through `E06`** — Read in order. Each experiment builds context for the next.
3. **`analysis.md`** — Read after experiments. The analysis cross-references experiments rather than reproducing them.
4. **`recommendation.md`** — Read last. It assumes familiarity with the findings.

This order ensures you encounter the evidence before the conclusions, which is the intended verification path for a grader or reviewer.
