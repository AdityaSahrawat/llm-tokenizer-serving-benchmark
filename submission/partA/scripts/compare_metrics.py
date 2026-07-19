#!/usr/bin/env python3
"""
compare_metrics.py -- multi-denominator fertility comparison

Computes four fertility denominators for each language corpus:
  tok/word  — tokens per whitespace-delimited word (corpus-level ratio)
  tok/char  — tokens per Unicode character (corpus-level ratio)
  tok/byte  — tokens per UTF-8 byte (corpus-level ratio)
  tok/sent  — tokens per sentence / parallel line (corpus-level ratio)

Usage:
    python compare_metrics.py \\
        --corpus eng=corpus/eng.txt \\
        --corpus hin=corpus/hin.txt \\
        --corpus kan=corpus/kan.txt \\
        --corpus tam=corpus/tam.txt \\
        --tokenizer hf:xlm-roberta-base \\
        --output results/denominator_comparison.csv

Notes on denominators:
  tok/word  Holds word count constant. Distorted cross-linguistically because
            word segmentation conventions differ between scripts.
  tok/char  Holds Unicode character count constant.
  tok/byte  Holds UTF-8 byte count constant. Indic script codepoints are
            3 bytes each; this denominator normalises for script byte-width.
  tok/sent  Holds semantic content constant (parallel alignment). The most
            controlled denominator for cross-lingual comparison.
"""

import argparse
import csv
import unicodedata
from pathlib import Path


def load_tokenizer(spec: str):
    if spec.startswith("hf:"):
        from transformers import AutoTokenizer
        tok = AutoTokenizer.from_pretrained(spec[3:])
        return lambda s: tok.encode(s, add_special_tokens=False)
    else:
        import tiktoken
        enc = tiktoken.get_encoding(spec)
        return enc.encode


def read_lines(path: str):
    lines = []
    with open(path, "r", encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()
            if not line:
                continue
            line = unicodedata.normalize("NFC", line)
            lines.append(line)
    return lines


def compute_metrics(lines, encode, lowercase: bool = True):
    """
    Return a dict of corpus-level ratios:
      tok_per_word, tok_per_char, tok_per_byte, tok_per_sent
    """
    total_tokens = 0
    total_words = 0
    total_chars = 0
    total_bytes = 0
    total_sents = len(lines)

    for line in lines:
        if lowercase:
            line = line.lower()
        tokens = encode(line)
        words = line.split()
        chars = len(line)
        byte_len = len(line.encode("utf-8"))

        total_tokens += len(tokens)
        total_words += len(words)
        total_chars += chars
        total_bytes += byte_len

    return {
        "tok_per_word": total_tokens / total_words if total_words > 0 else 0.0,
        "tok_per_char": total_tokens / total_chars if total_chars > 0 else 0.0,
        "tok_per_byte": total_tokens / total_bytes if total_bytes > 0 else 0.0,
        "tok_per_sent": total_tokens / total_sents if total_sents > 0 else 0.0,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--corpus",
        action="append",
        required=True,
        metavar="LANG=PATH",
        help="language code and path, e.g. eng=corpus/eng.txt (repeatable)",
    )
    ap.add_argument("--tokenizer", default="hf:xlm-roberta-base")
    ap.add_argument(
        "--lowercase",
        default="true",
        choices=["true", "false"],
        help="Apply lowercasing before tokenizing (default: true)",
    )
    ap.add_argument(
        "--output",
        default=None,
        metavar="PATH",
        help="Optional path to write results as CSV",
    )
    args = ap.parse_args()

    lowercase = args.lowercase.lower() == "true"
    encode = load_tokenizer(args.tokenizer)

    # Header
    print(f"\ntokenizer: {args.tokenizer}")
    print(f"lowercase: {args.lowercase}")
    col_w = 8
    print(
        f"{'lang':<{col_w}}"
        f"{'tok/word':>14}"
        f"{'tok/char':>12}"
        f"{'tok/byte':>12}"
        f"{'tok/sent':>12}"
    )
    print("-" * (col_w + 14 + 12 + 12 + 12))

    results = {}
    for spec in args.corpus:
        lang, path = spec.split("=", 1)
        lines = read_lines(path)
        m = compute_metrics(lines, encode, lowercase)
        results[lang] = m
        print(
            f"{lang:<{col_w}}"
            f"{m['tok_per_word']:>14.3f}"
            f"{m['tok_per_char']:>12.3f}"
            f"{m['tok_per_byte']:>12.3f}"
            f"{m['tok_per_sent']:>12.2f}"
        )

    # Relative comparison vs first language
    if len(results) >= 2:
        langs = list(results)
        base = langs[0]
        print()
        for lang in langs[1:]:
            r_word = results[lang]["tok_per_word"] / results[base]["tok_per_word"]
            r_byte = results[lang]["tok_per_byte"] / results[base]["tok_per_byte"]
            r_sent = results[lang]["tok_per_sent"] / results[base]["tok_per_sent"]
            word_dir = "worse" if r_word > 1 else "better"
            byte_dir = "worse" if r_byte > 1 else "better"
            sent_dir = "worse" if r_sent > 1 else "better"
            print(
                f"{lang} vs {base}: "
                f"tok/word={r_word:.2f}x ({word_dir})  "
                f"tok/byte={r_byte:.2f}x ({byte_dir})  "
                f"tok/sent={r_sent:.2f}x ({sent_dir})"
            )

    # Write CSV
    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["tokenizer", "lang", "tok_per_word", "tok_per_char",
                              "tok_per_byte", "tok_per_sent"])
            for lang, m in results.items():
                writer.writerow([
                    args.tokenizer,
                    lang,
                    f"{m['tok_per_word']:.4f}",
                    f"{m['tok_per_char']:.4f}",
                    f"{m['tok_per_byte']:.4f}",
                    f"{m['tok_per_sent']:.2f}",
                ])
        print(f"\nResults written to: {out_path}")


if __name__ == "__main__":
    main()
