import re

def split_sentence(text):
    sentences = re.split(r'(?<=[。！？.!?])', text)
    return [s.strip() for s in sentences if s.strip()]

