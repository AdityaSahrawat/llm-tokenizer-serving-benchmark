# Tokenizer Recommendation — Executive Memo

**To:** Engineering Leadership
**Re:** Tokenizer selection and Indic language serving cost

---

## Problem

The previous intern reported that Hindi tokenization costs approximately 6× more than English, and recommended budgeting 6× serving cost for all Indic traffic. This audit found that number to be incorrect. It was produced using the wrong tokenizer and an insufficient, non-parallel corpus.

---

## Headline Numbers

Using a multilingual tokenizer (XLM-RoBERTa) appropriate for production Indic serving, measured on 998 parallel sentences from FLORES-200:

| Language | Token cost vs English (per sentence) |
|----------|--------------------------------------|
| Hindi    | 1.24× English                        |
| Kannada  | 1.34× English                        |
| Tamil    | 1.33× English                        |

The correct overhead is **24–34% more tokens per request** for Indic languages — not 600%.

---

## Recommendation

**Deploy XLM-RoBERTa (or a similarly multilingual tokenizer) for all language tracks.** Do not use GPT-2 or any English-only tokenizer for Indic language serving. With a multilingual tokenizer, Indic language requests are manageable within standard infrastructure margins — a 30% token overhead does not require a separate fleet.

---

## Biggest Caveat

These measurements used Wikipedia-domain prose. Serving costs may differ on conversational input, short queries, or code-heavy prompts. Before committing infrastructure capacity, validate on a sample of actual production traffic in each language.

---

## Production Metric

Plan for **1.3× English token budget** per Indic language request as a conservative upper bound. Revisit if traffic analysis shows a different distribution of request lengths.
