# bambara_bpe_tokenizer.py
# Ni ye Bamankan Tokenizer module ye, I be se ka barake ni a ye ni ya wele niefe

import re
from collections import defaultdict, Counter
from typing import List, Tuple, Dict


class BambaraBPETokenizer:
    """
    A simple Byte Pair Encoding (BPE) tokenizer for the Bambara language.
    
    Steps:
      1. Learn BPE merges from a corpus
      2. Tokenize and detokenize text using learned rules
    """

    def __init__(self):
        self.vocab = Counter()
        self.bpe_codes = {}
        self.cache = {}

    def get_vocab(self, corpus: List[str]):
        """
        Builds the vocabulary as a dictionary of word-symbol frequency.
        """
        for line in corpus:
            words = line.strip().split()
            for word in words:
                word = " ".join(list(word)) + " </w>"
                self.vocab[word] += 1

    def get_stats(self) -> Dict[Tuple[str, str], int]:
        """
        Returns frequency of pairs of symbols.
        """
        pairs = defaultdict(int)
        for word, freq in self.vocab.items():
            symbols = word.split()
            for i in range(len(symbols) - 1):
                pairs[(symbols[i], symbols[i + 1])] += freq
        return pairs

    def merge_vocab(self, pair: Tuple[str, str]):
        """
        Merges the most frequent pair in the vocabulary.
        """
        bigram = re.escape(' '.join(pair))
        p = re.compile(r'(?<!\S)' + bigram + r'(?!\S)')
        new_vocab = {}
        for word in self.vocab:
            w_out = p.sub(''.join(pair), word)
            new_vocab[w_out] = self.vocab[word]
        self.vocab = new_vocab

    def learn_bpe(self, corpus: List[str], num_merges: int = 1000):
        """
        Learns BPE merge rules from a Bambara corpus.
        """
        self.get_vocab(corpus)
        for i in range(num_merges):
            pairs = self.get_stats()
            if not pairs:
                break
            best = max(pairs, key=pairs.get)
            self.bpe_codes[best] = i
            self.merge_vocab(best)

    def encode_word(self, word: str) -> List[str]:
        """
        Encodes a single word using learned BPE rules.
        """
        if word in self.cache:
            return self.cache[word]
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
        if word[-1] == '</w>':
            word = word[:-1]
        self.cache[word[0]] = word
        return word

    def encode(self, text: str) -> List[str]:
        """
        Encodes a Bambara sentence into BPE tokens.
        """
        words = text.strip().split()
        tokens = []
        for word in words:
            tokens.extend(self.encode_word(word))
        return tokens

    def decode(self, tokens: List[str]) -> str:
        """
        Decodes BPE tokens back into a string.
        """
        text = ' '.join(tokens)
        text = text.replace(' </w>', '')
        return text.replace('@@ ', '')

    def save(self, vocab_file: str, merges_file: str):
        """
        Saves the learned vocab and merges.
        """
        with open(vocab_file, 'w', encoding='utf-8') as vf:
            for word, freq in self.vocab.items():
                vf.write(f"{word} {freq}\n")
        with open(merges_file, 'w', encoding='utf-8') as mf:
            for pair, i in self.bpe_codes.items():
                mf.write(f"{pair[0]} {pair[1]}\n")
