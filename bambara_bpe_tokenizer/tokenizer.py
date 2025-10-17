import re
from collections import defaultdict, Counter
from typing import List, Tuple, Dict
import argparse

class BambaraBPETokenizer:
    """Minimal BPE tokenizer for the Bambara language."""

    def __init__(self):
        self.vocab = Counter()
        self.bpe_codes = {}
        self.cache = {}

    def get_vocab(self, corpus: List[str]):
        for line in corpus:
            words = line.strip().split()
            for word in words:
                word = " ".join(list(word)) + " </w>"
                self.vocab[word] += 1

    def get_stats(self) -> Dict[Tuple[str, str], int]:
        pairs = defaultdict(int)
        for word, freq in self.vocab.items():
            symbols = word.split()
            for i in range(len(symbols) - 1):
                pairs[(symbols[i], symbols[i + 1])] += freq
        return pairs

    def merge_vocab(self, pair: Tuple[str, str]):
        bigram = re.escape(' '.join(pair))
        p = re.compile(r'(?<!\S)' + bigram + r'(?!\S)')
        new_vocab = {}
        for word in self.vocab:
            w_out = p.sub(''.join(pair), word)
            new_vocab[w_out] = self.vocab[word]
        self.vocab = new_vocab

    def learn_bpe(self, corpus: List[str], num_merges: int = 1000):
        self.get_vocab(corpus)
        for i in range(num_merges):
            pairs = self.get_stats()
            if not pairs:
                break
            best = max(pairs, key=pairs.get)
            self.bpe_codes[best] = i
            self.merge_vocab(best)

    def encode_word(self, word: str) -> List[str]:
        if word in self.cache:
            return self.cache[word]
        original_word = word
        word = list(word) + ['</w>']
        pairs = [(word[i], word[i+1]) for i in range(len(word)-1)]

        while True:
            pair_freq = {pair: self.bpe_codes.get(pair, float('inf')) for pair in pairs}
            best = min(pair_freq, key=pair_freq.get)
            if best not in self.bpe_codes:
                break
            new_word = []
            i = 0
            while i < len(word):
                try:
                    j = word.index(best[0], i)
                    if j < len(word)-1 and word[j+1] == best[1]:
                        new_word.append(''.join(best))
                        i = j + 2
                    else:
                        new_word.append(word[i])
                        i += 1
                except:
                    new_word.extend(word[i:])
                    break
            word = new_word
            if len(word) == 1:
                break
            pairs = [(word[i], word[i+1]) for i in range(len(word)-1)]
        # Strip any boundary suffix that may have been merged into a token
        cleaned = []
        for token in word:
            if token.endswith('</w>'):
                cleaned.append(token[:-4])
            else:
                cleaned.append(token)
        # Remove a trailing empty token if stripping created one
        while cleaned and cleaned[-1] == '':
            cleaned.pop()
        word = cleaned
        # Safety: if merges/cleaning corrupted the token sequence, fallback to characters
        if ''.join(word) != original_word:
            word = list(original_word)
        # Cache by the original word to avoid collisions
        self.cache[original_word] = word
        return word

    def encode(self, text: str) -> List[str]:
        words = text.strip().split()
        tokens = []
        for word in words:
            # Emit a word boundary marker so we can faithfully decode spaces
            tokens.extend(self.encode_word(word))
            tokens.append('</w>')
        return tokens

    def decode(self, tokens: List[str]) -> str:
        words = []
        current = []
        for tok in tokens:
            if tok == '</w>':
                if current:
                    words.append(''.join(current))
                    current = []
                continue
            if tok.endswith('</w>'):
                current.append(tok[:-4])
                words.append(''.join(current))
                current = []
            else:
                current.append(tok)
        if current:
            words.append(''.join(current))
        return ' '.join(words).strip()


# --- CLI Interface ---
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Bambara BPE Tokenizer CLI")
    parser.add_argument("--train", type=str, help="Path to training corpus")
    parser.add_argument("--encode", type=str, help="Text to encode")
    parser.add_argument("--decode", type=str, help="Tokens to decode")
    parser.add_argument("--merges", type=int, default=1000, help="Number of BPE merges")
    args = parser.parse_args()

    bpe = BambaraBPETokenizer()

    if args.train:
        with open(args.train, encoding='utf-8') as f:
            corpus = f.readlines()
        bpe.learn_bpe(corpus, num_merges=args.merges)
        print(f"✅ Trained BPE model with {len(bpe.bpe_codes)} merges.")

    if args.encode:
        print("Encoded:", bpe.encode(args.encode))

    if args.decode:
        tokens = args.decode.split()
        print("Decoded:", bpe.decode(tokens))
