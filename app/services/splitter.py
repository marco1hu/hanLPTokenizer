import re

def split_sentence(text, max_len=40):
    rough_chunks = re.split(r'(?<=[。！？!?])', text)
    fine_chunks = []

    for chunk in rough_chunks:
        chunk = chunk.strip()
        if not chunk:
            continue

        while len(chunk) > max_len:
            fine_chunks.append(chunk[:max_len])
            chunk = chunk[max_len:]
        if chunk:
            fine_chunks.append(chunk)

    return fine_chunks
