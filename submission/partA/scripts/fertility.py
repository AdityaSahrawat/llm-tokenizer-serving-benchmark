#!/usr/bin/env python3
"""
fertility.py -- tokenizer fertility benchmark (corrected)

Computes tokenizer fertility (tokens per word) and compression
(tokens per character) for one or more language corpora.

Usage:
    python fertility.py --corpus eng=corpus/eng.txt \\
                        --corpus hin=corpus/hin.txt \\
                        --tokenizer hf:xlm-roberta-base \\
                        --lowercase true

Tokenizers:
    gpt2            -> tiktoken "gpt2" encoding (default)
    hf:<repo_id>    -> any HuggingFace tokenizer, e.g. hf:xlm-roberta-base

Flags:
    --lowercase true   Apply line.lower() before tokenizing (default: true)
    --lowercase false  Skip lowercasing; tokenize text as-is

Corrections over v0 (starterKit/fertility.py):
    1. Fertility is now computed as corpus-level ratio:
         total_tokens / total_words
       NOT as the mean of per-line ratios (sum(t_i/w_i) / n).
    2. Word splitting uses split() (any whitespace) instead of
       split(" ") (single space), which previously inflated word
       counts on lines with consecutive spaces.
    3. --lowercase flag allows controlled A/B comparison without
       editing source code.
"""

import argparse
import unicodedata


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


def analyze(lines, encode, lowercase: bool):
    """
    Return (fertility, tokens_per_char) as corpus-level ratios.

    fertility    = total_tokens / total_words   (corpus level)
    tok_per_char = total_tokens / total_chars   (corpus level)

    If lowercase is True, each line is lowercased before tokenizing.
    """
    total_tokens = 0
    total_words = 0
    total_chars = 0

    for line in lines:
        if lowercase:
            line = line.lower()
        tokens = encode(line)
        words = line.split()        # split() handles any whitespace, removes empties
        chars = len(line)

        total_tokens += len(tokens)
        total_words += len(words)
        total_chars += chars

    fertility = total_tokens / total_words if total_words > 0 else 0.0
    tpc = total_tokens / total_chars if total_chars > 0 else 0.0
    return fertility, tpc


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--corpus",
        action="append",
        required=True,
        metavar="LANG=PATH",
        help="language code and path, e.g. eng=corpus/eng.txt (repeatable)",
    )
    ap.add_argument("--tokenizer", default="gpt2")
    ap.add_argument(
        "--lowercase",
        default="true",
        choices=["true", "false"],
        help="Apply lowercasing before tokenizing (default: true)",
    )
    args = ap.parse_args()

    lowercase = args.lowercase.lower() == "true"
    encode = load_tokenizer(args.tokenizer)

    print(f"tokenizer:  {args.tokenizer}")
    print(f"lowercase:  {args.lowercase}")
    print(f"{'lang':<8}{'fertility (tok/word)':>22}{'tok/char':>12}")
    print("-" * 42)
    results = {}
    for spec in args.corpus:
        lang, path = spec.split("=", 1)
        lines = read_lines(path)
        fert, tpc = analyze(lines, encode, lowercase)
        results[lang] = (fert, tpc)
        print(f"{lang:<8}{fert:>22.2f}{tpc:>12.3f}")

    if len(results) >= 2:
        langs = list(results)
        base = langs[0]
        print()
        for lang in langs[1:]:
            ratio = results[lang][0] / results[base][0]
            print(
                f"{lang} is {ratio:.2f}x the fertility of {base} "
                f"({'worse' if ratio > 1 else 'better'} tokenization)"
            )


if __name__ == "__main__":
    main()
