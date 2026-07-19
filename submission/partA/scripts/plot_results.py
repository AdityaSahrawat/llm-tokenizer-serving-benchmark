#!/usr/bin/env python3
"""
plot_results.py -- Generate visualization plots for Part A results

Produces:
  1. submission/partA/results/plots/tokenizer_bar.png
     Bar chart comparing GPT-2 vs XLM-RoBERTa fertility (tok/word) across languages.
  2. submission/partA/results/plots/denominator_bar.png
     Bar chart comparing normalized denominator metrics relative to English under XLM-RoBERTa.
"""

import csv
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np


def plot_tokenizer_comparison(csv_path: Path, output_path: Path):
    langs = []
    gpt2_vals = []
    xlm_vals = []

    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            langs.append(row["lang"].upper())
            gpt2_vals.append(float(row["gpt2_tok_per_word"]))
            xlm_vals.append(float(row["xlm_tok_per_word"]))

    x = np.arange(len(langs))
    width = 0.35

    fig, ax = plt.subplots(figsize=(8, 5))
    rects1 = ax.bar(x - width / 2, gpt2_vals, width, label="GPT-2 (English-only)", color="#d9534f")
    rects2 = ax.bar(x + width / 2, xlm_vals, width, label="XLM-RoBERTa (Multilingual)", color="#5cb85c")

    ax.set_ylabel("Fertility (Tokens / Word)", fontsize=11, fontweight="bold")
    ax.set_title("Tokenizer Fertility Comparison Across Languages", fontsize=13, fontweight="bold", pad=15)
    ax.set_xticks(x)
    ax.set_xticklabels(langs, fontsize=11, fontweight="bold")
    ax.legend(fontsize=10)
    ax.grid(axis="y", linestyle="--", alpha=0.5)

    # Add data labels
    for rect in rects1:
        height = rect.get_height()
        ax.annotate(f"{height:.2f}",
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),  # 3 points vertical offset
                    textcoords="offset points",
                    ha="center", va="bottom", fontsize=9)

    for rect in rects2:
        height = rect.get_height()
        ax.annotate(f"{height:.2f}",
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),
                    textcoords="offset points",
                    ha="center", va="bottom", fontsize=9)

    plt.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"Saved plot: {output_path}")


def plot_denominator_comparison(csv_path: Path, output_path: Path):
    data = {}
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            lang = row["lang"]
            data[lang] = {
                "word": float(row["tok_per_word"]),
                "byte": float(row["tok_per_byte"]),
                "sent": float(row["tok_per_sent"]),
            }

    eng = data["eng"]
    langs = [l for l in data.keys() if l != "eng"]

    # Compute ratios relative to English
    rel_word = [data[l]["word"] / eng["word"] for l in langs]
    rel_byte = [data[l]["byte"] / eng["byte"] for l in langs]
    rel_sent = [data[l]["sent"] / eng["sent"] for l in langs]

    x = np.arange(len(langs))
    width = 0.25

    fig, ax = plt.subplots(figsize=(9, 5.5))
    ax.axhline(1.0, color="gray", linestyle="--", linewidth=1.5, label="English Baseline (1.0x)")

    r1 = ax.bar(x - width, rel_word, width, label="tok/word (Words)", color="#428bca")
    r2 = ax.bar(x, rel_byte, width, label="tok/byte (Bytes)", color="#5cb85c")
    r3 = ax.bar(x + width, rel_sent, width, label="tok/sent (Sentences)", color="#f0ad4e")

    ax.set_ylabel("Ratio Relative to English", fontsize=11, fontweight="bold")
    ax.set_title("Impact of Denominator Choice on Relative Language Cost (XLM-RoBERTa)", fontsize=12, fontweight="bold", pad=15)
    ax.set_xticks(x)
    ax.set_xticklabels([l.upper() for l in langs], fontsize=11, fontweight="bold")
    ax.legend(fontsize=10)
    ax.grid(axis="y", linestyle="--", alpha=0.5)

    for rects in (r1, r2, r3):
        for rect in rects:
            h = rect.get_height()
            ax.annotate(f"{h:.2f}x",
                        xy=(rect.get_x() + rect.get_width() / 2, h),
                        xytext=(0, 3),
                        textcoords="offset points",
                        ha="center", va="bottom", fontsize=8.5)

    plt.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"Saved plot: {output_path}")


def main():
    script_dir = Path(__file__).resolve().parent
    part_a_dir = script_dir.parent
    results_dir = part_a_dir / "results"
    plots_dir = results_dir / "plots"

    tok_csv = results_dir / "tokenizer_comparison.csv"
    den_csv = results_dir / "denominator_comparison.csv"

    if tok_csv.exists():
        plot_tokenizer_comparison(tok_csv, plots_dir / "tokenizer_bar.png")
    else:
        print(f"Warning: {tok_csv} not found")

    if den_csv.exists():
        plot_denominator_comparison(den_csv, plots_dir / "denominator_bar.png")
    else:
        print(f"Warning: {den_csv} not found")


if __name__ == "__main__":
    main()
