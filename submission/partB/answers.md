# B3 + B4 — Report Audit

---

## B3 — Intern Report Throughput Error

### Question

The intern's report states: *"at batch 16, long prompts hit 1311 tok/s vs only 883 tok/s for short prompts. Longer prompts clearly give better GPU utilization."*

Is 1311 tok/s the correct throughput number to report for a capacity planning decision? If not, what is the correct number and how is it derived?

---

### Evidence

From `bench_log.csv`, batch=16 rows:

| batch | prompt_len | gen_len | num_requests | wall_clock_s | reported_tok_s |
|---|---|---|---|---|---|
| 16 | 512  | 256 | 16 | 13.91 | 883.2  |
| 16 | 3584 | 512 | 16 | 49.97 | 1311.4 |

From `model_spec.md`:

> `reported_tok_s` — the harness's built-in throughput counter

---

### Misread Column

`reported_tok_s` counts **all tokens processed** by the model, including prompt tokens that are prefilled (processed once during the prefill phase but never returned to the user). For a request with `prompt_len=3584` and `gen_len=512`, the model processes `3584 + 512 = 4096` tokens total, but the client receives only `512` tokens.

`reported_tok_s` is therefore a measure of GPU throughput (how fast the model moves tokens through its layers), not **goodput** — the rate at which useful, newly generated tokens are delivered to users. For capacity planning — specifically, "how many user-facing output tokens per second can we deliver" — goodput is the correct metric.

The intern presented `reported_tok_s` as if it were goodput. It is not.

---

### Correct Calculation

**Method 1 — Direct from wall clock and generation counts**

```
Goodput = (num_requests × gen_len) / wall_clock_s
        = (16 × 512) / 49.97
        = 8192 / 49.97
        ≈ 163.9 tok/s
```

This is derived entirely from observable quantities in `bench_log.csv` without needing to interpret `reported_tok_s`.

**Method 2 — Scale reported_tok_s by the generation fraction**

The `reported_tok_s` counter counts all tokens, but only `gen_len / (prompt_len + gen_len)` of those are newly generated. Therefore:

```
Goodput = reported_tok_s × gen_len / (prompt_len + gen_len)
        = 1311.4 × 512 / (3584 + 512)
        = 1311.4 × 512 / 4096
        = 1311.4 × 0.125
        ≈ 163.9 tok/s
```

Both methods produce the same result, which cross-validates the calculation.

---

### Independent Verification

For the short-prompt row (batch=16, prompt=512, gen=256):

- Method 1: `(16 × 256) / 13.91 = 4096 / 13.91 ≈ 294.6 tok/s`
- Method 2: `883.2 × 256 / (512 + 256) = 883.2 × 256 / 768 = 883.2 × 0.333 ≈ 294.4 tok/s`

Both methods agree again (~294 tok/s). This confirms the formula is consistent across prompt configurations.

---

### Correct Report Wording

The intern's sentence:

> *"at batch 16, long prompts hit 1311 tok/s vs only 883 tok/s for short prompts"*

should be replaced with:

> *"At batch=16, the system delivers approximately **164 tok/s of user-facing output throughput** on long-prompt workloads (prompt=3584, gen=512). The harness reports 1311 tok/s of total token throughput, but this includes prefilled prompt tokens; the generation goodput — the metric relevant to capacity planning — is 164 tok/s. The equivalent figure for short-prompt workloads (prompt=512, gen=256) is 295 tok/s."*

---

## B4 — Validation Metric for B2

### Metric

**`preempted_seqs`** (combined with `kv_cache_util`).

### Why This Metric

A serving system operating within its KV cache budget should have `preempted_seqs = 0` for all batch sizes that fit in memory. Preemptions are a direct, observable consequence of KV cache exhaustion: the scheduler cannot be forced to preempt unless it has run out of KV blocks to allocate. `kv_cache_util` shows how full the cache is; `preempted_seqs` shows whether the scheduler actually exceeded that limit. Together, they bracket the saturation threshold.

### Expected Value

The B2 analysis (in `throughput_analysis.md`) identifies batch=24 as the last operating point before saturation. The B1 prediction (in `kv_cache_math.md`) predicts a maximum of 27 concurrent 4096-token sequences before KV exhaustion.

Expected observations:

| batch | preempted_seqs | kv_cache_util |
|---|---|---|
| ≤ 24 | 0 | < 0.95 |
| ≥ 32 | > 0 | ≥ 0.97 |

### How It Validates B2

The benchmark log confirms this exactly:

- batch=24: `preempted_seqs=0`, `kv_cache_util=0.93` — fits the prediction (no preemptions, below saturation).
- batch=32: `preempted_seqs=7`, `kv_cache_util=0.97` — confirms KV exhaustion starts between 24 and 32 sequences, consistent with the B1 prediction of 27.
- batch=48: `preempted_seqs=23`, `kv_cache_util=0.97` — saturation confirmed; throughput degrades as predicted.

The transition from `preempted_seqs=0` to `preempted_seqs>0` at batch=32 is the empirical signal that the system has crossed the KV cache capacity boundary. This validates both the B1 prediction (27 sequences ≈ between 24 and 32) and the B2 recommendation (cap at batch=24).
