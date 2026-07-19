# E04 — Average Ratio Bug

**Evidence for claim:** "The intern's `analyze()` function computes fertility as the mean of per-line ratios rather than as the ratio of corpus totals, which is mathematically incorrect and biases results toward shorter lines."

---

## Question

Does the method of computing fertility — `mean(tokens_i / words_i)` vs `sum(tokens_i) / sum(words_i)` — produce materially different results?

## Hypothesis

`mean(tokens_i / words_i)` is the average of per-line fertility values. This gives equal weight to every sentence regardless of length. A two-word sentence and a twenty-word sentence count equally. `sum(tokens_i) / sum(words_i)` is the corpus-level ratio: total tokens divided by total words. This weights each sentence proportionally to its word count. On a corpus with variable sentence lengths, these two quantities are not equal. The corpus-level ratio is the standard definition of fertility in the NLP literature. The per-line average is a bias toward short sentences, which tend to have higher fertility because tokenizer overhead is amortised differently. We expect the corpus-level ratio to be lower than the per-line average.

---

## Method

The intern's original `analyze()` accumulates per-line ratios and returns `sum(per_line_fertility) / n`. The corrected version accumulates `total_tokens` and `total_words` and returns `total_tokens / total_words`. Run both on all four corpora with XLM-RoBERTa and compare.

---

## Command

```bash
# Buggy — per-line mean (intern's original code)
# analyze() returns: sum(per_line_fertility) / n
uv run python starterKit/fertility.py \
  --corpus eng=submission/partA/corpus/eng.txt \
  --corpus hin=submission/partA/corpus/hin.txt \
  --corpus kan=submission/partA/corpus/kan.txt \
  --corpus tam=submission/partA/corpus/tam.txt \
  --tokenizer hf:xlm-roberta-base

# Corrected — corpus-level ratio
# analyze() returns: total_tokens / total_words
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
# Buggy — per-line mean
tokenizer: hf:xlm-roberta-base
lang      fertility (tok/word)    tok/char
------------------------------------------
eng                       1.41       0.236
hin                       1.49       0.292
kan                       2.46       0.301
tam                       2.41       0.268
```

```
# Corrected — corpus-level ratio
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

- The per-line mean is consistently slightly lower than the corpus-level ratio by approximately 0.01–0.02 across all languages.
- English: 1.41 vs 1.42 (per-line mean underestimates by 0.7%).
- Hindi: 1.49 vs 1.50 (per-line mean underestimates by 0.7%).
- Kannada: 2.46 vs 2.47 (per-line mean underestimates by 0.4%).
- Tamil: 2.41 vs 2.42 (per-line mean underestimates by 0.4%).
- The direction of bias is consistent: the per-line mean always underestimates the correct corpus-level ratio on this corpus.

---

## Conclusion

The intern's `analyze()` function is methodologically incorrect. Fertility is defined as `total_tokens / total_words` at the corpus level, not as the mean of per-line ratios. The per-line mean underestimates fertility by approximately 0.5–0.7% on this corpus. The effect is small enough that relative conclusions about language rankings remain unchanged, but the absolute numbers are biased and the code does not match the standard definition. The corrected `fertility.py` uses the corpus-level ratio.
