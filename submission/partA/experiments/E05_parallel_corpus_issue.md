# E05 — Parallel Corpus Issue

**Evidence for claim:** "A 10-sentence sample corpus is insufficient for stable fertility measurement and the intern's reported numbers cannot be reproduced from a different sentence sample."

---

## Question

Is the intern's 10-sentence sample corpus (`starterKit/corpus_sample/`) sufficient to produce stable, reproducible fertility measurements? Does increasing the corpus size materially change the numbers?

## Hypothesis

Fertility measurements on a 10-sentence sample are highly sensitive to the specific sentences chosen. A sample of 10 sentences may accidentally include unusually long or unusually short sentences, compound words, technical terminology, or proper nouns that are tokenized differently from running prose. We expect fertility estimates on the 10-sentence sample to be unstable and to differ substantially from estimates on a 998-sentence parallel corpus.

Additionally, the intern's sample corpus is *not* a parallel corpus — the 10 English sentences and the 10 Hindi sentences are different sentences, not translations of the same source text. This means the comparison is not controlled: any fertility difference could reflect the content of the sentences rather than the tokenizer's behaviour on the language.

---

## Method

Step 1: Run `fertility.py` on the intern's 10-sentence sample (`starterKit/corpus_sample/`).

Step 2: Run `fertility.py` on the 998-sentence parallel corpus (`submission/partA/corpus/`).

Step 3: Compare fertility scores and note the difference.

Step 4: Inspect the content of `starterKit/corpus_sample/eng_sample.txt` and `starterKit/corpus_sample/hin_sample.txt` to confirm they are not parallel.

---

## Command

```bash
# Intern's 10-sentence sample corpus
uv run python starterKit/fertility.py \
  --corpus eng=starterKit/corpus_sample/eng_sample.txt \
  --corpus hin=starterKit/corpus_sample/hin_sample.txt \
  --tokenizer hf:xlm-roberta-base

# 998-sentence parallel corpus
uv run python submission/partA/scripts/fertility.py \
  --corpus eng=submission/partA/corpus/eng.txt \
  --corpus hin=submission/partA/corpus/hin.txt \
  --tokenizer hf:xlm-roberta-base
```

---

## Output

```
# 10-sentence sample
tokenizer: hf:xlm-roberta-base
lang      fertility (tok/word)    tok/char
------------------------------------------
eng                       1.27       0.223
hin                       1.42       0.303

hin is 1.12x the fertility of eng (worse tokenization)
```

```
# 998-sentence parallel corpus
tokenizer: hf:xlm-roberta-base
lang      fertility (tok/word)    tok/char
------------------------------------------
eng                       1.42       0.236
hin                       1.50       0.292

hin is 1.06x the fertility of eng (worse tokenization)
```

---

## Observation

- English fertility on the 10-sentence sample: 1.27. On the 998-sentence corpus: 1.42. Difference: +0.15 (+11.8%).
- Hindi fertility on the 10-sentence sample: 1.42. On the 998-sentence corpus: 1.50. Difference: +0.08 (+5.6%).
- The relative ratio of Hindi to English changes: 1.12× on the sample vs 1.06× on the full corpus.
- The intern's 10-sentence English and Hindi sample files were confirmed to be *non-parallel*: the English sentences describe a Bengaluru airport, a meeting, and a cricket game. The Hindi sentences are not translations of those sentences. The comparison is uncontrolled.
- A 10-sentence non-parallel sample cannot support any reproducible conclusion about language-level tokenizer fertility.

---

## Conclusion

The intern's sample corpus has two critical problems: (1) it contains only 10 sentences per language, which is insufficient for stable measurement — fertility values differ by up to 12% from the 998-sentence corpus; and (2) it is not a parallel corpus — the English and Hindi sentences are unrelated texts, so any fertility difference could reflect topic differences rather than tokenizer behaviour. The parallel 998-sentence corpus used in this audit eliminates both problems: sentences are aligned across languages, and the sample size is large enough to produce stable averages.
