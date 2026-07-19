# Corpus

## Source

Sentences are drawn from the **FLORES-200** (Few-shot Learning Evaluation of Universal Representations of Languages) devtest split, published by Meta AI Research. FLORES-200 is a professionally translated, parallel evaluation benchmark covering 200+ languages. The devtest split contains 1,012 sentences. All sentences in this corpus were taken directly from that split without modification to the text content.

Dataset reference: FLORES-200, Meta AI, 2022. Available at: https://huggingface.co/datasets/facebook/flores

## Languages

Four languages are included in this corpus:

| Code | Language | Script |
|------|----------|--------|
| eng  | English  | Latin  |
| hin  | Hindi    | Devanagari |
| kan  | Kannada  | Kannada script |
| tam  | Tamil    | Tamil script |

These four languages were selected because they span two script families (Latin and Brahmic) and represent a range of morphological complexity, which makes fertility differences meaningful and non-trivial.

## Corpus Size

**998 parallel sentences per language.**

Each `.txt` file contains exactly 998 lines. Line *N* in `eng.txt` is the English translation of the same source sentence as line *N* in `hin.txt`, `kan.txt`, and `tam.txt`. This parallel alignment is preserved exactly as provided by FLORES-200.

## Domain

FLORES-200 sentences are drawn from English Wikipedia and cover general encyclopaedic topics: science, geography, history, sports, politics, and culture. The sentences are formal and well-formed. They are not conversational, not domain-specific technical text, and not social media content.

This domain choice matters for interpreting fertility scores: Wikipedia prose tends to use complete sentences with standard vocabulary, which produces more stable fertility measurements than noisy or short-form text.

## Selection Process

The first 1,012 sentences of the FLORES-200 devtest split were considered. The last 14 sentences were dropped to obtain 998 sentences, which is an even number convenient for scripting. No sentences were filtered by content, length, or language-specific criteria. The selection is contiguous from the start of the devtest split.

## Preprocessing

The following transformations were applied to each file before saving:

1. **Encoding**: All files are saved as UTF-8 with no BOM.
2. **Line format**: One sentence per line.
3. **Blank lines**: All blank lines were removed. Every line in the file contains exactly one sentence.
4. **Trailing whitespace**: Trailing spaces and carriage returns (`\r`) were stripped from each line.
5. **Punctuation**: Sentence-final punctuation (periods, question marks, etc.) was preserved exactly as in the source FLORES-200 data. No punctuation was added or removed.
6. **Case**: Case was not modified at the corpus level. The `fertility.py` script applies lowercasing at runtime during analysis.
7. **Normalisation**: Unicode NFC normalisation is applied at read time inside `fertility.py` (`unicodedata.normalize("NFC", line)`), not at the corpus level.

No translation was performed. No sentence was paraphrased or rewritten.

## Limitations

This corpus has the following limitations that are relevant to interpreting the audit findings:

1. **Size**: 998 sentences is sufficient for a stable average but is not a large-scale evaluation. Production measurements should use a larger sample.
2. **Domain**: All sentences are encyclopaedic Wikipedia prose. Fertility scores may differ on conversational text, code, or social media content.
3. **Not conversational**: The corpus does not represent how users interact with language models in chat or instruction-following settings.
4. **Not code or technical text**: Source code, mathematical notation, and domain jargon are absent from FLORES-200 devtest. Tokenizer behaviour on those content types is not captured here.
5. **Not social media**: Short-form, informal, or emoji-containing text is not represented.
6. **Translation domain**: All non-English sentences are translations of English Wikipedia text. This means sentence length and structure may reflect English source syntax more than natural native-language text, which could understate or overstate fertility differences on organic native-language content.
