# Part A — Technical Analysis

## Introduction

This document contains the technical audit of the intern's tokenizer fertility measurements (A2) and the corrected analysis using a reproducible, parallel corpus and appropriate tokenizer (A3). Every claim in this document is backed by an experiment in `experiments/`. Where evidence is referenced, the experiment file is cited directly. No experimental output is reproduced here.

---

## A2 — Script Audit

The intern's `fertility.py` (version 0, located at `starterKit/fertility.py`) was inspected for correctness. Four issues were identified: three bugs and one harmless suspicious item.

---

### Issue 1 — Incorrect Averaging Method

**What the code does:** `analyze()` computes fertility as the arithmetic mean of per-line fertility values: `sum(tokens_i / words_i) / n`.

**What it should do:** Fertility is defined as the corpus-level ratio: `sum(tokens_i) / sum(words_i)`.

**Why this is wrong:** The per-line mean gives equal weight to every sentence regardless of its length. On a corpus with variable sentence lengths, this is not equivalent to the corpus-level ratio. The per-line mean is biased toward shorter sentences, which tend to have different fertility characteristics from longer ones.

**Magnitude:** Approximately 0.5–0.7% underestimation on this corpus.

**Evidence:** See E04.

---

### Issue 2 — Whitespace Split

**What the code does:** `words = line.split(" ")` — splits on a literal single space.

**What it should do:** `words = line.split()` — splits on any whitespace sequence and discards empty strings.

**Why this is wrong:** If any line contains two or more consecutive spaces, `split(" ")` produces empty string elements in the resulting list, which inflates the word count and deflates fertility. The FLORES-200 corpus contains occasional double spaces.

**Magnitude:** Approximately 0.4–0.7% underestimation on this corpus.

**Evidence:** See E03.

---

### Issue 3 — Inappropriate Corpus

**What the corpus is:** 10 non-parallel sentences per language, sourced from unspecified locations, stored in `starterKit/corpus_sample/`.

**What it should be:** A parallel corpus of sufficient size (hundreds of sentences), where line *N* in every language file is a translation of the same source sentence.

**Why this is wrong:** A 10-sentence non-parallel sample has two problems: it is too small to produce a stable fertility estimate (fertility varies by up to 12% depending on sentence selection), and the non-parallel design means any fertility difference could reflect topic or vocabulary differences between the samples rather than tokenizer behaviour on the language.

**Evidence:** See E05.

---

### Harmless Suspicious Code

**What the code does:** `random.seed(1337)` is set at module level.

**Why it is suspicious:** Setting a random seed suggests the code may use random sampling, which would introduce non-determinism without the seed. However, inspection of the full script reveals no call to any random function. The seed call is a no-op.

**Assessment:** Harmless. The random seed has no effect on any computation. It is likely a copy-paste artefact from an earlier version of the script. It can be removed without changing any result.

---

## A3 — Corrected Analysis

The corrected analysis uses:

- A 998-sentence parallel corpus drawn from FLORES-200 devtest (see `corpus/README.md`).
- The XLM-RoBERTa tokenizer (`hf:xlm-roberta-base`), which has multilingual vocabulary coverage for all four languages tested.
- The corrected `fertility.py` script: corpus-level ratio (`total_tokens / total_words`), `split()` for word segmentation.

---

### Tokenizer Comparison

GPT-2 produces fertility values of 5.35×, 7.00×, and 6.83× relative to English for Hindi, Kannada, and Tamil respectively. XLM-RoBERTa produces 1.06×, 1.75×, and 1.71×. The intern's conclusion of approximately 6× worse fertility for Hindi is an artefact of using GPT-2, which has no Indic vocabulary. On a multilingual tokenizer appropriate for the task, the gap is substantially smaller.

**Evidence:** See E01.

---

### Denominator Comparison

Three denominators were measured. The results differ qualitatively:

- **tok/word**: Indic languages are 1.06×–1.75× English. Biased by differences in morphological word length across scripts.
- **tok/byte**: Indic languages are 0.42×–0.48× English — *better* than English. Indic script characters take 3 UTF-8 bytes; the tokenizer handles them efficiently, so fewer tokens are emitted per raw byte.
- **tok/sent**: Indic languages are 1.24×–1.34× English. This is the most controlled denominator: since all corpora are parallel, tok/sent measures the token cost of expressing the same semantic content.

**Evidence:** See E06.

---

### Recommendation

The tok/sent denominator under XLM-RoBERTa on the parallel corpus is the most defensible number for production capacity planning. Under this metric, Indic language requests cost approximately 24%–34% more tokens than equivalent English requests — not 6× as the intern reported. The 6× figure was produced by combining two methodological errors: using GPT-2 on Indic text and using a non-parallel 10-sentence sample.

The recommendation for production deployment is in `recommendation.md`.
