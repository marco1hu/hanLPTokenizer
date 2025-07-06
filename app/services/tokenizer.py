import hanlp

_tokenizer = hanlp.load('LARGE_ALBERT_BASE')

def tokenize_text(text):
    return [token.strip() for token in _tokenizer(text)]
