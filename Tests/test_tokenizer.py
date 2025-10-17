from bambara_bpe_tokenizer.tokenizer import BambaraBPETokenizer

def test_basic_encoding():
    corpus = ["A bɛ taa", "N’a fɛ ka kɛ nyɛ"]
    tokenizer = BambaraBPETokenizer()
    tokenizer.learn_bpe(corpus, num_merges=50)

    encoded = tokenizer.encode("A bɛ taa")
    decoded = tokenizer.decode(encoded)

    assert isinstance(encoded, list)
    assert decoded.strip() == "A bɛ taa"
