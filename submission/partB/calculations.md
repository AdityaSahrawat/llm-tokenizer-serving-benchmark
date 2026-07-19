# calculations.md — KV Cache Arithmetic (Engineering Notebook)

---

## Section 1 — KV Cache Memory Per Token

### Known Values

```
layers           = 28
KV_heads         = 8
head_dim         = 128
tensors (K + V)  = 2
bytes/element    = 2   (fp16)
```

### Step 1 — bytes per element

```
fp16 → 2 bytes/element
```

### Step 2 — bytes per (K or V) vector per layer

```
KV_heads × head_dim = 8 × 128 = 1024 elements/layer
1024 × 2 bytes      = 2048 bytes per K (or V) vector, per layer
```

### Step 3 — bytes per token per layer (K + V)

```
2048 × 2 tensors = 4096 bytes / (token × layer)
```

### Step 4 — bytes per token (all layers)

```
4096 × 28 layers = 114,688 bytes/token
                 = 112 KB/token
```

---

## Section 2 — Memory Budget

### Starting point

```
GPU VRAM                  = 24 GB
```

### Step 1 — usable memory after gpu_memory_utilization

```
24 × 0.92 = 22.08 GB  (usable)
```

### Step 2 — subtract runtime overhead

```
22.08 − 1.6 = 20.48 GB  (after activations, CUDA graphs, etc.)
```

### Step 3 — model weight size

```
Parameters  = 4.2 × 10^9
Precision   = fp16 = 2 bytes/param
Weight size = 4.2 × 10^9 × 2 = 8.4 × 10^9 bytes = 8.4 GB
```

### Step 4 — remaining KV memory

```
20.48 − 8.4 = 12.08 GB  (available for KV cache)
```

### Step 5 — convert to bytes

```
12.08 × 1024^3 = 12.08 × 1,073,741,824
              = 12,971,241,267.2 bytes
              ≈ 12,971,241,267 bytes
```

---

## Section 3 — Prediction: Maximum Concurrent Sequences

### Step 1 — bytes per sequence (max_model_len = 4096 tokens)

```
114,688 bytes/token × 4096 tokens = 469,762,048 bytes/sequence
                                  = 448.0 MB/sequence
```

*Exact:*
```
114,688 × 4096 = 114,688 × 4000 + 114,688 × 96
               = 458,752,000 + 11,010,048
               = 469,762,048 bytes
```

### Step 2 — maximum concurrent sequences

```
KV_memory   = 12,971,241,267 bytes
seq_memory  = 469,762,048 bytes

max_seqs = floor(12,971,241,267 / 469,762,048)
         = floor(27.61...)
         = 27
```

*Division check:*
```
27 × 469,762,048 = 12,683,575,296  (fits)
28 × 469,762,048 = 13,153,337,344  (exceeds 12,971,241,267 → does not fit)
```

**Prediction: 27 concurrent 4096-token sequences maximum.**

---

## Section 4 — Cross-Check Against Benchmark Log

### Observed peak (from bench_log.csv, long-prompt rows)

```
batch=24, prompt=3584, gen=512  → kv_cache_util = 0.93
batch=32, prompt=3584, gen=512  → kv_cache_util = 0.97  (also: preempted_seqs = 7)
batch=48, prompt=3584, gen=512  → kv_cache_util = 0.97  (also: preempted_seqs = 23)
```

### Tokens in flight at batch=24 (peak of non-preempted operation)

```
total tokens per sequence (max) = prompt_len + gen_len = 3584 + 512 = 4096
sequences in flight             = 24
total tokens                    = 24 × 4096 = 98,304 tokens
```

### Implied capacity at kv_cache_util = 0.93

```
If 24 sequences → 93% utilization:
total capacity = 24 / 0.93 = 25.8 sequences

If 27 sequences → 100% utilization (predicted)
Implied util at 24 seqs = 24 / 27 = 0.889 ≈ 0.89
```

### Comparison

```
Predicted max sequences  : 27
Implied from kv_util=0.93: 25.8
Difference               : 27 − 25.8 = 1.2 sequences
Relative error           : 1.2 / 25.8 ≈ 4.7%
```

*The benchmark saturates at kv_cache_util=0.97, implying the scheduler*
*uses capacity slightly more conservatively than our theoretical maximum.*
*The prediction (27) is within ~5% of the observed saturation point (~25-26).*
