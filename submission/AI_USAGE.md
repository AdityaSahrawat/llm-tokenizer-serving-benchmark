# AI Usage

## Overview

AI assistance was used throughout this project as a pair-programming and brainstorming tool. Every claim that appears in a results file was experimentally verified before inclusion. AI did not run any experiment, read any file, or produce any output that was included without my independent verification of the underlying numbers.

The workflow was:

```
AI suggestion or hypothesis
        ↓
Form a testable question
        ↓
Write or modify the script
        ↓
Run the command
        ↓
Compare output to prediction
        ↓
Accept, reject, or revise
```

No result in `analysis.md`, `calculations.md`, or any experiment file came from AI output alone. Every table, every number, every conclusion has a command in the `experiments/` directory or `calculations.md` that produced it.

---

## Where AI Helped

**Brainstorming potential audit issues.** When I first read the intern's script, I listed the lines that looked suspicious. AI helped me think through which issues were likely to matter and which were probably harmless — for example, it flagged the `split(" ")` vs `split()` distinction before I had measured it, which directed my attention to the right place.

**Explaining tokenizer concepts.** I had a rough understanding of subword tokenization but AI clarified the relationship between SentencePiece vocabulary coverage and fertility for non-Latin scripts, and explained why a multilingual tokenizer's byte-pair encodings align with Unicode codepoint boundaries for Indic scripts. This shaped how I framed the denominator comparison.

**Organising the report structure.** AI suggested the separation between `calculations.md` (raw arithmetic) and `kv_cache_math.md` (polished B1 answer), and the experiment file template (Question → Hypothesis → Method → Command → Output → Observation → Conclusion). These structural decisions improved the reviewability of the submission.

**Reviewing mathematical derivations.** After working through the KV cache memory budget manually, I used AI to check whether I had missed any terms (e.g., whether activation memory needed to be subtracted separately from the KV budget). In this case AI's check agreed with my own derivation.

**Improving writing.** AI helped tighten the language in `recommendation.md` and `memo.md`, particularly in making the executive summaries concise enough to read without context.

---

## Where AI Was Wrong

**Overestimating the impact of lowercasing.** Early in the audit, AI suggested that `line.lower()` could introduce meaningful distortion in fertility scores because lowercasing changes how tokenizers handle proper nouns and sentence-initial capitals. I expected a non-trivial effect. The experiment showed a 0.7% difference for English and no measurable difference for Indic scripts. AI's concern was plausible in principle but incorrect for this tokenizer and corpus. I documented this in E02 as a "harmless suspicious code" item and rejected lowercasing as a significant error source.

**Initial uncertainty about the direction of tok/byte.** When I asked about the tok/byte denominator, AI hedged on whether Indic scripts would produce more or fewer tokens per byte than Latin scripts. I expected the answer to be "more tokens per byte" (consistent with tok/word). The experiment showed the opposite: XLM-RoBERTa produces *fewer* tokens per UTF-8 byte for Hindi, Kannada, and Tamil than for English. AI's uncertainty here forced me to run the experiment rather than trust the hypothesis. The result is documented in E06.

**Arithmetic conservatism on the KV memory budget.** When I described the memory budget calculation, AI initially suggested budgeting a larger overhead figure (~2–3 GB) for activations and CUDA graphs. The problem statement specifies 1.6 GB. I used the specified value rather than the AI-suggested estimate, which changes the predicted maximum sequence count from ~23 to ~27. I reported the number derived from the given spec, not AI's conservative estimate.

---

## Verification Process

For every experiment in `partA/experiments/`:

1. Formed the question independently (or confirmed an AI-suggested question was worth testing).
2. Wrote or modified the script myself (the `--lowercase` flag addition, the `split()` fix, the corpus-level ratio formula).
3. Ran the command exactly as written in the experiment file.
4. Compared the output to the hypothesis before writing the conclusion.
5. If the result contradicted the hypothesis, revised the hypothesis and noted the surprise in the notebook.

For Part B arithmetic in `calculations.md`:

1. Worked through every multiplication and subtraction by hand before checking with AI.
2. Verified each intermediate result against the next step (e.g., checked that 27 × 469,762,048 < 12,971,241,267 < 28 × 469,762,048).
3. Cross-checked the prediction (27 sequences) against `bench_log.csv` (saturation between batch=24 and batch=32).

---

## What I Personally Understand

I can explain every part of this submission without AI assistance during a defense:

- **The fertility formula** and why `total_tokens / total_words` differs from `mean(tokens_i / words_i)`, with a numerical example.
- **Why tok/byte reverses** the language ranking relative to tok/word, and what that means for how you model serving cost.
- **The KV cache memory derivation** from first principles: where each term (layers, heads, head_dim, K+V, bytes/element) comes from and how they compound.
- **Why the throughput anomaly occurs** at batch=32: the scheduler preemption mechanism, KV block exhaustion, and why adding more concurrent requests past the saturation point reduces rather than increases throughput.
- **Why 1311 tok/s is the wrong number** for the intern's capacity planning claim: the distinction between total model throughput and user-facing goodput, with two independent calculations that give 164 tok/s.
- **Every script modification** in `submission/partA/scripts/fertility.py`: what each change fixes, why the original was wrong, and what the corrected version does differently.
