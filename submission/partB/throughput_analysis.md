# B2 — Throughput Analysis

## Section 1 — Observation

The benchmark runs two corpus types: short prompts (512 tokens, 256 generation) and long prompts (3584 tokens, 512 generation). The table below focuses on the long-prompt rows, which are the only ones that exhibit a throughput anomaly.

| batch | reported_tok_s | preempted_seqs | kv_cache_util |
|---|---|---|---|
| 4  | 565.4  | 0  | 0.16 |
| 8  | 902.6  | 0  | 0.31 |
| 16 | 1311.4 | 0  | 0.62 |
| 24 | 1607.4 | 0  | 0.93 |
| 32 | 1384.0 | 7  | 0.97 |
| 48 | 1298.5 | 23 | 0.97 |

Throughput increases with batch size from 4 through 24, then **falls** at batch 32 and falls further at batch 48, despite more sequences being present.

---

## Section 2 — Anomaly

Throughput peaks at **batch=24 (1607 tok/s)** and then declines:

```
batch 24 → 1607.4 tok/s   (peak)
batch 32 → 1384.0 tok/s   (−14% from peak)
batch 48 → 1298.5 tok/s   (−19% from peak)
```

The intern's report interpreted the data incorrectly: it cited the batch=16 long-prompt value (1311 tok/s) and the batch=16 short-prompt value (883 tok/s) and concluded "longer prompts give better GPU utilization" and that "batch 48 should give ~3200 tok/s". Both conclusions are wrong. Throughput does *not* scale linearly with batch size beyond the KV cache saturation point, and batch=48 delivers *less* throughput than batch=24.

---

## Section 3 — Evidence

The three anomalous rows (batch=32, batch=48) show a consistent pattern across all latency and utilisation signals simultaneously:

| batch | preempted_seqs | kv_cache_util | ttft_ms_p50 | itl_ms_p50 |
|---|---|---|---|---|
| 24 | 0  | 0.93 | 500.5 | 96.1  |
| 32 | 7  | 0.97 | 636.9 | 101.8 |
| 48 | 23 | 0.97 | 955.4 | 100.0 |

All four metrics increase together at the transition from batch=24 to batch=32:

- `preempted_seqs`: rises from 0 to 7 (batch=32) and 23 (batch=48). Sequences that were partially generated had their KV cache evicted and had to wait.
- `kv_cache_util`: jumps from 0.93 to 0.97 and saturates. The cache is full; no new sequences can be admitted without evicting an existing one.
- `ttft_ms_p50`: rises from 500 ms to 637 ms (+27%) and 955 ms (+91%). Requests wait longer to even start generating because no KV block is available.
- `itl_ms_p50`: increases from 96 ms to 102 ms (+6%). Decode stalls while the scheduler resolves block pressure.

This correlated increase across all four signals confirms that a single underlying constraint is responsible: the KV cache is saturated.

---

## Section 4 — Mechanism

**KV cache saturation.** Each sequence requires 448 MB of KV cache at full 4096-token length (see `kv_cache_math.md`). The system has approximately 12.08 GB of KV memory, supporting roughly 27 full sequences. At batch=24, utilization is 0.93 — the cache is nearly full but not yet exhausted. At batch=32, the 32nd sequence cannot be fully admitted; the scheduler must preempt an in-flight sequence (evict its KV blocks) to make room.

**Scheduler preemption.** vLLM's scheduler (and similar systems) use a swap or recompute strategy when KV blocks are exhausted. When a new request must be admitted and no blocks are free, an existing sequence's blocks are evicted to secondary storage (or dropped for recompute). That sequence resumes only when blocks become available again. This adds latency for both the preempted sequence (which must wait to resume) and new requests (which wait in queue while the scheduler resolves the conflict).

**Why throughput falls.** The reported throughput counter measures tokens generated per wall-clock second. When the scheduler is spending time preempting, evicting, and re-scheduling sequences rather than generating tokens, the GPU is idle during those windows. Additionally, preempted sequences must regenerate previously computed KV states (recompute strategy) or reload them from slower memory (swap strategy), both of which reduce effective token generation rate. The net result is that adding more batch pressure beyond the KV saturation point reduces throughput even though more requests are nominally "in flight".

---

## Section 5 — Recommendation

**Set `max_num_seqs` to 24 for this workload.**

The benchmark shows that batch=24 is the last operating point with zero preemptions (`kv_cache_util = 0.93`). Constraining the scheduler to admit at most 24 concurrent sequences prevents KV cache exhaustion and keeps throughput at its peak value of **1607 tok/s**.

Quantitative effect of this change:
- Throughput: maintains 1607 tok/s vs the degraded 1298–1384 tok/s observed at batch=32–48.
- TTFT p50: holds at ~500 ms vs 637–955 ms.
- Preemptions: 0 vs 7–23 per run.

If higher throughput is required, the correct lever is to increase the KV cache budget — either by using a GPU with more VRAM, enabling quantised KV cache (e.g., INT8), or reducing `max_model_len` to admit more concurrent shorter sequences. Increasing batch size beyond the KV ceiling does not improve throughput on this configuration.
