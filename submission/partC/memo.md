# Decision Memo — Conversational Tone Adaptation

**To:** Engineering & Product Leadership
**Date:** 2026-07-19
**Re:** Approach selection for reducing formality in multilingual model outputs

---

## 1. Problem Summary

The product team reports that model outputs in Hindi, Kannada, and Tamil are perceived as excessively formal by end-users in casual conversation contexts. English outputs exhibit the same issue but to a lesser degree. Users expect responses that match the register of everyday spoken language rather than formal written prose.

Three candidate approaches have been identified to address this: prompt engineering, supervised fine-tuning (SFT) on synthetic casual examples, and preference-based fine-tuning (RLHF/DPO). A decision is required on which approach to pursue under current resource and timeline constraints.

---

## 2. Constraints

| Constraint | Value |
|---|---|
| GPU | 1× NVIDIA L4 (24 GB, same as serving GPU) |
| Human reviewer capacity | Part-time: ~10 hours/week |
| Timeline to first deployed experiment | ≤ 4 weeks |
| Budget | No additional GPU spend — use existing L4 |
| Languages | English, Hindi, Kannada, Tamil |
| Model | FLM-4B-Instruct (4.2B parameters, fp16) |
| Serving throughput baseline | ~164 tok/s goodput at batch=16 (from Part B) |
| Latency tolerance | Current p95 at batch=16: ~55 s |

---

## 3. Assumptions

The following are not given in the brief and are stated explicitly so they can be challenged:

1. **Synthetic data quality:** A capable general-purpose LLM (GPT-4 class) can generate sufficiently casual rewrites of formal outputs to serve as SFT training pairs. Quality is assumed acceptable without human rewriting of every example — only spot-check review.
2. **Reviewer throughput:** A part-time reviewer at 10 hours/week can review approximately 30 examples/hour (binary accept/reject), yielding ~300 reviewed examples/week.
3. **Minimum viable SFT dataset:** 200 high-quality (prompt, casual response) pairs per language (800 total) are sufficient for a v1 style-transfer fine-tune on a 4B-parameter model. This assumption has not been validated on this specific model.
4. **Training feasibility on L4:** A 4B fp16 model can be fine-tuned with LoRA on 24 GB VRAM. Full fp16 fine-tuning would not fit; LoRA or QLoRA is assumed.
5. **No inference latency regression:** A LoRA adapter merged into base weights before deployment adds zero latency overhead at serving time.
6. **Preference signal not required at this stage:** The formality gap is well-defined enough that SFT on (formal → casual) pairs moves the distribution without pairwise preference labels.
7. **Casual tone is language-specific:** Casual register in Hindi, Kannada, and Tamil differs structurally. Language-tagged training examples are assumed sufficient to address this without separate per-language models.
8. **No regulatory risk:** Reducing output formality does not create a compliance concern for this product use case.

---

## 4. Candidate Solutions

| Approach | Advantages | Disadvantages | Estimated Cost | Risk |
|---|---|---|---|---|
| **A. Prompt engineering** | No training cost. Deployable in hours. Reversible. | Inconsistent across conversation turns. Increases prompt token count → higher KV cache pressure. Limited style shift at 4B scale. | Zero hardware. 1–2 engineer-days. | Low technical. Medium product (inconsistency). |
| **B. SFT on synthetic data** | Persistent style change across all turns. Per-language coverage. Fits L4 with LoRA. Proven approach for style transfer. | Requires data generation, review, training pipeline. 3–4 week setup. Synthetic data may miss edge-case registers. | ~2 GPU-hours training. 5–6 reviewer-weeks. | Medium: depends on synthetic data quality (§3.1). |
| **C. RLHF / DPO** | Highest quality ceiling. Directly optimises user preference signal. | Requires pairwise labels — 2–3× slower than binary review. Needs reward model or DPO pipeline. Timeline infeasible. | ~60–80 GPU-hours. 20+ reviewer-weeks. | High: timeline exceeds constraint by 5–10×. |

---

## 5. Chosen Solution

**Approach B — Supervised fine-tuning on synthetic casual data.**

**Why B over A:** Prompt-based style control at 4B scale does not maintain consistent register across multi-turn conversations. Additionally, adding a system-level style instruction increases average prompt length. At the Part B observed KV utilisation (0.93 at batch=24), even modest prompt inflation risks crossing the preemption threshold identified in `throughput_analysis.md`. SFT produces a persistent change with no per-request overhead.

**Why B over C:** RLHF/DPO requires pairwise preference labels across four languages. At 10–15 comparisons/hour, collecting 1,000 comparisons per language requires 25–40 reviewer-weeks. The 4-week constraint eliminates this option entirely. DPO also requires a training pipeline more complex than SFT and carries higher risk of over-optimisation on sparse feedback.

**Why B is viable:** LoRA fine-tuning of a 4B model fits on the L4 (§6.3). Synthetic data can be generated in hours. A v1 dataset of 800 reviewed examples is achievable within 5–6 reviewer-weeks, with a training-ready subset of 400 examples by week 4 if review begins immediately.

---

## 6. Back-of-the-Envelope Calculations

### 6.1 Data — Example Count

```
Target (v1)          : 200 accepted examples × 4 languages = 800 total
Generation ratio     : 2:1 (generate 2, accept 1 after pre-filter + review)
Total to generate    : 800 × 2 = 1,600 examples
Generation speed     : ~200 examples/hour (batch API)
Generation time      : 1,600 / 200 = 8 hours  (automated, no human time)
```

### 6.2 Reviewer — Time Budget

```
Reviewer capacity    : 10 hours/week
Review rate          : 30 examples/hour (binary accept/reject)
Examples reviewed/wk : 10 × 30 = 300 examples/week

Review pool          : 1,600 generated examples
Time to review all   : 1,600 / 300 = 5.3 reviewer-weeks

Accepted output      : 800 examples (50% accept rate assumed)
```

Week 4 checkpoint: after 4 reviewer-weeks, ~1,200 examples reviewed → ~600 accepted. Sufficient for a first training run (150/language).

### 6.3 GPU — Training Time

```
Model size (fp16)    : 4.2B × 2 bytes = 8.4 GB
LoRA rank=16 adapter : ~20M params — negligible additional memory
Activations (est.)   : ~4–5 GB at batch_size=4, seq_len=512
Total GPU memory     : ~13–14 GB  → fits on 24 GB L4

Dataset              : 800 examples
Epochs               : 3
Steps                : (800 × 3) / 4 = 600 steps
Time/step (est.)     : ~4 seconds on L4 (fp16 forward + backward, 4B model)
Total training time  : 600 × 4 = 2,400 s ≈ 0.67 hours

With eval + checkpoints: ~2 GPU-hours per full run
```

Well within L4 availability. Three training iterations (v1, v1.1, v2) fit in a single day.

### 6.4 Serving — Latency Impact

LoRA adapters merged via `merge_and_unload()` produce a model identical in architecture and parameter count to the base model. Inference computational graph is unchanged. No latency regression expected.

Current baseline (Part B, batch=16, long-prompt): p95 latency = 54,602 ms. Post-deployment target: remain within 10% of this value (≤ 60,000 ms p95).

---

## 7. Success Metric

| | |
|---|---|
| **Metric** | Human-rated casual register acceptance rate |
| **Target** | ≥ 70% of outputs rated "acceptable casual register" across all four languages; no single language below 60% |
| **Measurement** | Reviewer labels 100 randomly sampled model outputs per language (400 total) as "casual / natural" or "too formal". Blind: reviewer does not know which model produced the output. |
| **Baseline** | Run the same evaluation on the un-fine-tuned base model before training. Expected baseline: < 30% casual-acceptable (per product team report of widespread formality). |
| **Why this metric** | It directly measures the product requirement. Automated metrics (BLEU, perplexity) do not correlate with casual register perception. The evaluation is feasible within reviewer time: 400 samples at 30/hour = ~13 reviewer-hours. |

---

## 8. Kill Criterion

**Observation:** After training on the full v1 dataset (≥ 600 reviewed examples), the 100-sample evaluation returns fewer than 50% casual-acceptable outputs in any single language.

**Decision:** Abandon SFT v1. Do not continue iterating with the same data generation pipeline. The synthetic data quality assumption (§3.1) has failed.

**Immediate action:** Deploy Approach A (prompt engineering) as a short-term mitigation. Re-scope the data strategy — either recruit native-language reviewers to rewrite examples manually, or switch to a higher-quality generation model — and revisit SFT in the following quarter.

**Deadline:** End of week 5 (training completes week 4; evaluation completes week 5). A decision must be made by end of week 5 regardless of in-progress reviewer work.

---

## 9. Day-1 Experiment

**Objective:** Validate that the synthetic data generation pipeline produces casual outputs that are reliably distinguishable from the base model's formal outputs by a human reviewer, before investing reviewer time in large-scale labelling.

**Method:**

1. Generate 20 (formal prompt → casual response) pairs per language (80 synthetic examples total).
2. Run the same 80 prompts through the base model to produce 80 formal outputs.
3. Interleave all 160 outputs randomly, remove labels, and present to the reviewer.
4. Reviewer labels each as "casual" or "formal" without knowing the source.

**Expected outcome:** ≥ 75% of synthetic examples labelled "casual"; ≥ 85% of base model outputs labelled "formal". If either threshold is not met, the data generation approach must be revised before scaling.

**Time cost:** ~3 reviewer-hours. Produces a go/no-go signal on the data pipeline on day 1, before any significant resource is committed.

---

## 10. Risks

| Risk | Likelihood | Mitigation |
|---|---|---|
| Synthetic casual data fails to generalise to real user conversational inputs | Medium | Generate from diverse prompt types (greeting, follow-up, correction, request). Evaluate on 20 real user samples before deployment. |
| LoRA fine-tuning degrades task accuracy on factual queries while improving casual register | Medium | Evaluate on 50 factual Q&A samples per language before and after every training run. Include factual Q&A in training mix if degradation is observed. |
| Reviewer bottleneck delays v1 dataset beyond week 5 | High | Begin review immediately in week 1. Define a 400-example week-4 checkpoint sufficient for a first training run. Do not wait for full dataset before first iteration. |
| Tamil and Kannada casual register poorly represented in generation model output | Medium | Recruit one native reviewer per Dravidian language for spot-check validation of generated examples, rather than relying on a single general-purpose reviewer. |
| Merged LoRA adapter causes unexpected output distribution shift on non-casual queries | Low | Run regression evaluation on 50 held-out task-completion samples per language after merge, before production deployment. |

---

## 11. Final Recommendation

Proceed with **supervised fine-tuning (SFT) using LoRA** on 800 synthetic casual examples reviewed by a part-time human reviewer, targeting a first training run in week 4.

Prompt engineering (Approach A) is eliminated because it does not produce persistent multi-turn register control and adds token overhead that encroaches on the serving system's KV cache margin — already at 93% utilisation at the batch size where goodput peaks. Preference-based tuning (Approach C) exceeds reviewer capacity by an order of magnitude and cannot be delivered within four weeks.

The SFT approach is executable within constraints: training requires ~14 GB GPU memory (fits on L4), costs ~2 GPU-hours per run, and the review pipeline produces a training-ready dataset within 4–5 weeks if review begins on day 1. The Day-1 experiment (§9) validates the data pipeline within hours at minimal cost. The kill criterion (§8) limits open-ended iteration to one additional week after training.

**Immediate next actions:**
1. Begin synthetic data generation today (automated, ~8 hours).
2. Start reviewer binary labelling in week 1.
3. Run Day-1 experiment (§9) within the first two days.
4. Schedule training run for week 4 on the 400-example checkpoint.
5. Complete success evaluation (§7) by end of week 5.
