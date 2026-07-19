# E06 — Denominator Comparison

**Evidence for claim:** "The choice of denominator (tok/word, tok/byte, tok/sent) holds different quantities constant and leads to meaningfully different conclusions about relative tokenization quality."

---

## Question

Which fertility denominator is most appropriate for comparing tokenization quality across languages with different scripts and morphology?

## Hypothesis

Three denominators are possible:

- **tok/word**: tokens divided by whitespace-delimited word count. Holds the "number of words" constant. Appropriate when comparing within the same language or script family. Problematic cross-linguistically because word segmentation conventions differ: agglutinative languages pack more meaning per word.
- **tok/byte**: tokens divided by UTF-8 byte count. Holds raw text volume constant. Normalises for the fact that Indic script characters take 3 bytes in UTF-8 while Latin characters take 1 byte. A multilingual tokenizer that produces fewer tokens per byte is more efficient for serving.
- **tok/sent**: tokens divided by sentence count. Holds the "unit of meaning" constant, since each line in a parallel corpus is a translation of the same source sentence. This is the most controlled comparison: it asks how many tokens are required to express the same semantic content in each language.

We expect tok/word and tok/sent to tell similar stories (Indic languages worse than English), but tok/byte to partially reverse the ranking because Indic scripts are byte-expensive.

---

## Method

Run `compare_metrics.py` on all four corpora with XLM-RoBERTa. This script computes all three denominators in one pass.

---

## Command

```bash
uv run python submission/partA/scripts/compare_metrics.py \
  --corpus eng=submission/partA/corpus/eng.txt \
  --corpus hin=submission/partA/corpus/hin.txt \
  --corpus kan=submission/partA/corpus/kan.txt \
  --corpus tam=submission/partA/corpus/tam.txt \
  --tokenizer hf:xlm-roberta-base
```

---

## Output

```
tokenizer: hf:xlm-roberta-base
lang      fertility (tok/word)    tok/char    tok/byte    tok/sent
------------------------------------------------------------------
eng                       1.42       0.236       0.235       29.58
hin                       1.50       0.292       0.114       36.75
kan                       2.47       0.301       0.111       39.74
tam                       2.42       0.268       0.098       39.23

hin is 1.06x the fertility (tok/word) of eng (worse tokenization)
hin is 0.48x the tok/byte of eng (better tokenization per UTF-8 byte)
hin is 1.24x the tok/sent of eng (worse tokenization per parallel sentence)
kan is 1.75x the fertility (tok/word) of eng (worse tokenization)
kan is 0.47x the tok/byte of eng (better tokenization per UTF-8 byte)
kan is 1.34x the tok/sent of eng (worse tokenization per parallel sentence)
tam is 1.71x the fertility (tok/word) of eng (worse tokenization)
tam is 0.42x the tok/byte of eng (better tokenization per UTF-8 byte)
tam is 1.33x the tok/sent of eng (worse tokenization per parallel sentence)
```

---

## Observation

**tok/word**
Indic languages are worse than English by a factor of 1.06×–1.75×. This denominator is distorted by the fact that Indic languages (particularly Kannada and Tamil, which are agglutinative) express more meaning per "word", so the comparison is not linguistically fair.

**tok/byte**
All three Indic languages produce *fewer* tokens per UTF-8 byte than English (0.42×–0.48× English). This is because Indic script characters take 3 bytes each in UTF-8, while the tokenizer's SentencePiece vocabulary aligns well with those multi-byte characters. This denominator shows XLM-RoBERTa is byte-efficient for Indic scripts.

**tok/sent**
Indic languages require 1.24×–1.34× more tokens than English to express the same sentence (controlled by parallel alignment). This is the most meaningful denominator for serving cost estimation: if a request is "translate this sentence," the relevant question is how many tokens that sentence costs in each language.

The three denominators tell qualitatively different stories. tok/sent is recommended for serving cost projection because it is controlled for semantic content via parallel alignment.

---

## Conclusion

Denominator choice is not a detail — it changes the conclusion. Under tok/byte, all Indic languages appear *better* than English (fewer tokens per byte), which could lead to the wrong serving cost model. Under tok/word, the intern's framing of "worse tokenization" is supported but not at the magnitude the intern claimed. Under tok/sent — the most controlled denominator for a parallel corpus — Indic languages cost 24%–34% more tokens per sentence than English when using XLM-RoBERTa. This is the number most relevant to production capacity planning. The tok/char column (included for completeness) confirms the script-level story: Indic scripts pack more semantic content per character.
