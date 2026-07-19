# Submission

## Assignment Overview

This submission audits a previous intern's tokenizer fertility measurements and serving throughput report, then produces a corrected analysis and a product decision memo. Part A audits and corrects the tokenizer fertility benchmark: identifying bugs in the analysis script, rebuilding the corpus from a proper parallel source, and measuring fertility under both an English-only and a multilingual tokenizer across four languages. Part B audits the serving benchmark log: deriving KV cache capacity from model specifications, identifying the cause of the throughput anomaly at high batch sizes, and correcting the intern's misreading of the throughput column. Part C produces a structured decision memo recommending an approach for improving conversational tone in multilingual model outputs, with explicit assumptions, back-of-the-envelope arithmetic, a measurable success criterion, and a kill criterion.

---

## Repository Structure

```
submission/
│
├── README.md               ← This file
├── NOTEBOOK.md             ← First-person lab notebook: hypotheses, experiments, revisions
├── AI_USAGE.md             ← Honest account of AI assistance and verification process
│
├── partA/                  ← Tokenizer audit (A1–A3)
│   ├── README.md           ← Navigation and reproduction guide for Part A
│   ├── analysis.md         ← Technical report: script audit (A2) and corrected analysis (A3)
│   ├── recommendation.md   ← Executive memo: one-page production recommendation
│   ├── corpus/             ← 998-line FLORES-200 parallel corpus (eng, hin, kan, tam)
│   ├── scripts/            ← Corrected fertility.py, compare_metrics.py, run_analysis.sh
│   ├── experiments/        ← E01–E06: one experiment file per hypothesis tested
│   └── results/            ← Generated CSVs and plots (produced by run_analysis.sh)
│
├── partB/                  ← Serving audit (B1–B4)
│   ├── calculations.md     ← Every arithmetic step: KV math, memory budget, prediction
│   ├── kv_cache_math.md    ← B1 polished answer: formula, derivation, validation
│   ├── throughput_analysis.md  ← B2: observation, anomaly, evidence, mechanism, fix
│   └── answers.md          ← B3 + B4: goodput correction and validation metric
│
└── partC/                  ← Decision memo (C)
    └── memo.md             ← 11-section structured recommendation
```

**`partA/`** — All work relating to tokenizer fertility. The `corpus/` subdirectory contains the raw text; `scripts/` contains executable code; `experiments/` contains the evidence trail; `results/` contains generated outputs.

**`partB/`** — All work relating to serving throughput and KV cache capacity. `calculations.md` and `kv_cache_math.md` separate raw arithmetic from polished explanation. `throughput_analysis.md` and `answers.md` address B2–B4 respectively.

**`partC/`** — A single decision memo organised as a management document: constraints, assumptions, candidate comparison, recommendation, arithmetic, success metric, kill criterion, and day-1 experiment.

---

## Quick Navigation

| Want to read | File |
|---|---|
| Part A — technical audit findings | [partA/analysis.md](partA/analysis.md) |
| Part A — production recommendation | [partA/recommendation.md](partA/recommendation.md) |
| Part A — experiment evidence (E01–E06) | [partA/experiments/](partA/experiments/) |
| Part B — KV cache calculation (B1) | [partB/kv_cache_math.md](partB/kv_cache_math.md) |
| Part B — KV cache raw arithmetic | [partB/calculations.md](partB/calculations.md) |
| Part B — throughput anomaly (B2) | [partB/throughput_analysis.md](partB/throughput_analysis.md) |
| Part B — goodput correction + validation (B3, B4) | [partB/answers.md](partB/answers.md) |
| Part C — decision memo | [partC/memo.md](partC/memo.md) |
| Lab notebook (thinking process) | [NOTEBOOK.md](NOTEBOOK.md) |
| AI usage disclosure | [AI_USAGE.md](AI_USAGE.md) |
| Corpus source and preprocessing | [partA/corpus/README.md](partA/corpus/README.md) |
| Corrected fertility script | [partA/scripts/fertility.py](partA/scripts/fertility.py) |

---

## How to Reproduce

**Prerequisites:**

```bash
# Python 3.11+, uv package manager
uv sync
```

**Run the full Part A pipeline:**

```bash
bash submission/partA/scripts/run_analysis.sh
```

**Or run individual scripts manually:**

```bash
# Corrected fertility — XLM-RoBERTa
uv run python submission/partA/scripts/fertility.py \
  --corpus eng=submission/partA/corpus/eng.txt \
  --corpus hin=submission/partA/corpus/hin.txt \
  --corpus kan=submission/partA/corpus/kan.txt \
  --corpus tam=submission/partA/corpus/tam.txt \
  --tokenizer hf:xlm-roberta-base \
  --lowercase true

# Denominator comparison
uv run python submission/partA/scripts/compare_metrics.py \
  --corpus eng=submission/partA/corpus/eng.txt \
  --corpus hin=submission/partA/corpus/hin.txt \
  --corpus kan=submission/partA/corpus/kan.txt \
  --corpus tam=submission/partA/corpus/tam.txt \
  --tokenizer hf:xlm-roberta-base
```

**Part B** does not require scripts — all calculations are in `partB/calculations.md` and reference `starterKit/bench/bench_log.csv` directly.

---

## Summary

All conclusions in this submission are supported by experiments with exact commands and observed outputs. No conclusion rests on a single measurement: wherever possible, two independent methods were used to derive the same result (see B3 in `answers.md` for an explicit example). Raw data from the intern's benchmark (`starterKit/bench/bench_log.csv`) and model specification (`starterKit/bench/model_spec.md`) are preserved unmodified. The corrected analysis scripts in `partA/scripts/` are fully reproducible from the command lines documented in `partA/README.md` and in the individual experiment files.
