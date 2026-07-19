# B1 — KV Cache Memory Analysis

## Problem

Given the FLM-4B-Instruct model configuration and the L4 GPU serving setup, calculate the KV cache memory consumed per token, determine how much GPU memory is available for the KV cache after accounting for model weights and runtime overhead, and predict the maximum number of concurrent 4096-token sequences the system can serve before the KV cache is exhausted.

---

## Known Model Parameters

| Property | Value |
|---|---|
| Layers | 28 |
| KV Heads (GQA) | 8 |
| Head Dimension | 128 |
| KV Cache Precision | fp16 |
| Max Model Length | 4096 tokens |

| Hardware/Config | Value |
|---|---|
| GPU | NVIDIA L4, 24 GB |
| `gpu_memory_utilization` | 0.92 |
| Non-KV runtime overhead | ~1.6 GB |
| Model weights (4.2B × fp16) | 8.4 GB |

---

## Formula

Each token's KV cache must store one key vector and one value vector per layer. For a model with grouped-query attention:

```
Bytes/token = layers × KV_heads × head_dim × 2 (K and V) × bytes_per_element
```

This formula derives from the fact that every transformer layer independently maintains key and value projections for all KV heads, and each projection is a vector of length `head_dim` stored in the specified floating-point precision.

---

## Applying the Formula

Substituting the model parameters:

```
Bytes/token = 28 × 8 × 128 × 2 × 2
```

Detailed arithmetic is provided in `calculations.md`.

**Result: 114,688 bytes/token (112 KB/token)**

---

## Memory Budget

Starting from the 24 GB GPU:

```
24.00 GB  — total GPU VRAM
× 0.92    — gpu_memory_utilization
─────────
22.08 GB  — usable memory

 − 1.60 GB — non-KV runtime overhead
─────────
20.48 GB  — after overhead

 − 8.40 GB — model weights (4.2B params × 2 bytes)
─────────
12.08 GB  — available for KV cache
```

Detailed subtraction is in `calculations.md`.

---

## Maximum Concurrent Sequences

Memory required to hold the full KV cache for one 4096-token sequence:

```
114,688 bytes/token × 4096 tokens = 448 MB/sequence
```

Maximum concurrent sequences before KV cache exhaustion:

```
floor(12.08 GB / 0.448 GB) = floor(26.96...) = 27
```

Full division is in `calculations.md`.

**Prediction: 27 concurrent 4096-token sequences.**

---

## Validation Against Benchmark

From `bench_log.csv`, long-prompt rows (prompt=3584, gen=512, total=4096 tokens/sequence):

| batch | kv_cache_util | preempted_seqs |
|---|---|---|
| 16 | 0.62 | 0 |
| 24 | 0.93 | 0 |
| 32 | 0.97 | 7 |
| 48 | 0.97 | 23 |

The benchmark reaches `kv_cache_util = 0.93` at batch=24 without any preemptions, and saturates at 0.97 at batch=32 where preemption begins. This implies the scheduler fills approximately 24–26 sequences before hitting the KV ceiling.

The theoretical prediction of 27 sequences is within ~5% of the empirically observed saturation point. The small difference arises from the scheduler's block-allocation granularity and practical conservatism — it does not fill to exactly 100% utilization before triggering preemptions.

---

## Final Answer

| Quantity | Value |
|---|---|
| KV cache memory per token | 114,688 bytes (112 KB) |
| Available KV memory | 12.08 GB |
| Predicted max concurrent 4096-token sequences | 27 |
| Observed saturation (benchmark) | ~25–26 sequences (kv_util → 0.97 at batch=32) |
