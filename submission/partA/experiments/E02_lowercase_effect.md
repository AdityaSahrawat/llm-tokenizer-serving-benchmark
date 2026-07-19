# E02 — Lowercase Effect

**Evidence for claim:** "Lowercasing is a harmless preprocessing step that has negligible effect on fertility scores for the languages tested."

---

## Question

Does the lowercasing applied inside `analyze()` (line `line = line.lower()`) materially change fertility scores, or is it a safe preprocessing step?

## Hypothesis

Lowercasing reduces vocabulary variation from capitalisation but does not change token boundaries for most subword tokenizers. For Indic scripts (Devanagari, Kannada script, Tamil script), lowercasing is a no-op because those scripts have no case distinction. For English, the effect should be small because most running text is already lowercase except for sentence-initial capitals and proper nouns. We expect a change of less than 1% in fertility for all four languages.

---

## Method

Run `fertility.py` with XLM-RoBERTa on all four corpora twice: once with `--lowercase true` and once with `--lowercase false`. Hold all other arguments constant. Compare the tok/word column.

The `--lowercase` flag was added specifically to make this comparison reproducible from the CLI without modifying source code.

---

## Command

```bash
# With lowercasing
uv run python submission/partA/scripts/fertility.py \
  --corpus eng=submission/partA/corpus/eng.txt \
  --corpus hin=submission/partA/corpus/hin.txt \
  --corpus kan=submission/partA/corpus/kan.txt \
  --corpus tam=submission/partA/corpus/tam.txt \
  --tokenizer hf:xlm-roberta-base \
  --lowercase true

# Without lowercasing
uv run python submission/partA/scripts/fertility.py \
  --corpus eng=submission/partA/corpus/eng.txt \
  --corpus hin=submission/partA/corpus/hin.txt \
  --corpus kan=submission/partA/corpus/kan.txt \
  --corpus tam=submission/partA/corpus/tam.txt \
  --tokenizer hf:xlm-roberta-base \
  --lowercase false
```

---

## Output

```
# With lowercase
tokenizer: hf:xlm-roberta-base
lang      fertility (tok/word)    tok/char
------------------------------------------
eng                       1.41       0.236
hin                       1.49       0.292
kan                       2.46       0.301
tam                       2.41       0.268
```

```
# Without lowercase
tokenizer: hf:xlm-roberta-base
lang      fertility (tok/word)    tok/char
------------------------------------------
eng                       1.42       0.237
hin                       1.49       0.292
kan                       2.46       0.301
tam                       2.41       0.268
```

---

## Observation

- English fertility changes from 1.41 to 1.42 — a difference of 0.01 (0.7%).
- Hindi, Kannada, and Tamil fertility are unchanged at all decimal places shown.
- The change is below measurement noise for any practical capacity planning decision.

---

## Conclusion

Lowercasing is a safe preprocessing step for this corpus and this tokenizer. It has negligible effect on fertility scores across all four languages tested. The intern's use of `line.lower()` is not a source of error. This line of the script is harmless.
