# E03 — Whitespace Split Bug

**Evidence for claim:** "The intern's script uses `split(' ')` (single space) rather than `split()` (any whitespace), which inflates word count in lines containing multiple consecutive spaces, producing slightly lower fertility values than correct."

---

## Question

Does replacing `line.split(" ")` with `line.split()` change fertility scores? Is the original `split(" ")` a bug?

## Hypothesis

`split(" ")` splits on a single space character and preserves empty strings between consecutive spaces. A line with two consecutive spaces (`"foo  bar"`) would produce `["foo", "", "bar"]` (3 words) instead of the correct `["foo", "bar"]` (2 words). This inflates the word count denominator and therefore deflates the fertility score. `split()` — with no argument — splits on any whitespace sequence and removes empty strings. We expect fertility to be slightly higher with `split()` for corpora containing any multi-space sequences.

---

## Method

Inspect the intern's `fertility.py` source for the split call. Run the corrected script (using `split()`) against the original (using `split(" ")`) and compare tok/word on all four languages with XLM-RoBERTa.

---

## Command

```bash
# Original — split(" ") — buggy behaviour
# (edit scripts/fertility.py line 63 to use split(" "))
uv run python submission/partA/scripts/fertility.py \
  --corpus eng=submission/partA/corpus/eng.txt \
  --corpus hin=submission/partA/corpus/hin.txt \
  --corpus kan=submission/partA/corpus/kan.txt \
  --corpus tam=submission/partA/corpus/tam.txt \
  --tokenizer hf:xlm-roberta-base

# Corrected — split() — correct behaviour
# (default in corrected script)
uv run python submission/partA/scripts/fertility.py \
  --corpus eng=submission/partA/corpus/eng.txt \
  --corpus hin=submission/partA/corpus/hin.txt \
  --corpus kan=submission/partA/corpus/kan.txt \
  --corpus tam=submission/partA/corpus/tam.txt \
  --tokenizer hf:xlm-roberta-base
```

---

## Output

```
# split(" ") — original
tokenizer: hf:xlm-roberta-base
lang      fertility (tok/word)    tok/char
------------------------------------------
eng                       1.41       0.236
hin                       1.49       0.292
kan                       2.46       0.301
tam                       2.41       0.268
```

```
# split() — corrected
tokenizer: hf:xlm-roberta-base
lang      fertility (tok/word)    tok/char
------------------------------------------
eng                       1.42       0.236
hin                       1.50       0.292
kan                       2.47       0.301
tam                       2.42       0.268
```

---

## Observation

- English: 1.41 → 1.42 (difference: +0.01, +0.7%)
- Hindi: 1.49 → 1.50 (difference: +0.01, +0.7%)
- Kannada: 2.46 → 2.47 (difference: +0.01, +0.4%)
- Tamil: 2.41 → 2.42 (difference: +0.01, +0.4%)
- The `split(" ")` bug underestimates fertility by approximately 0.5–0.7% across all languages.

---

## Conclusion

`split(" ")` is a latent bug. It inflates the word count in sentences with double spaces, producing a slightly deflated fertility value. The effect is small (under 1%) on this corpus, but the code is semantically wrong. The correct implementation uses `split()` with no argument. The corrected `fertility.py` in `scripts/` uses `split()`. The intern's report numbers are slightly underestimated as a result of this bug, but the relative conclusions are not materially affected on this corpus.
