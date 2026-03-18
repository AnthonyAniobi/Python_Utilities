def split_text_to_chunks(text: str, max_chars: int) -> list:
    """
    Split text into chunks guided by max_chars without ever cutting a word.
 
    Strategy:
      - Walk words one by one, accumulating into the current chunk.
      - When adding the next word would push the chunk past max_chars, decide
        whether to include it by picking whichever side is *closer* to max_chars.
        This means a chunk may end up slightly above OR slightly below the limit —
        but no word is ever split.
    """
    words = text.split()
    if not words:
        return []
 
    chunks = []
    current_words = []
    current_len = 0  # character count of the current chunk (spaces included)
 
    for word in words:
        word_len = len(word)
        # length if we append this word (add 1 for the separating space)
        new_len = current_len + (1 if current_words else 0) + word_len
 
        if not current_words:
            # always start with at least one word
            current_words.append(word)
            current_len = word_len
        elif new_len <= max_chars:
            # still within limit — keep building
            current_words.append(word)
            current_len = new_len
        else:
            # over limit: pick the boundary closer to max_chars
            overshoot  = new_len    - max_chars   # cost of including the word
            undershoot = max_chars  - current_len # cost of stopping here
 
            if overshoot <= undershoot:
                # including the word is closer to the target → add & flush
                current_words.append(word)
                chunks.append(" ".join(current_words))
                current_words = []
                current_len = 0
            else:
                # stopping before the word is closer → flush, then start new chunk
                chunks.append(" ".join(current_words))
                current_words = [word]
                current_len = word_len
 
    if current_words:
        chunks.append(" ".join(current_words))
 
    return chunks
 
 
def split_segment(seg: dict, max_chars: int) -> list:
    """
    Split a single Whisper segment into sub-segments.
    Timestamps are distributed proportionally by character count so timing
    stays as accurate as possible.
    """
    text = seg["text"].strip()
    if len(text) <= max_chars:
        return [seg]
 
    chunks = split_text_to_chunks(text, max_chars)
    if len(chunks) <= 1:
        return [seg]
 
    total_chars = sum(len(c) for c in chunks)
    duration    = seg["end"] - seg["start"]
    result      = []
    cursor      = seg["start"]
 
    for i, chunk in enumerate(chunks):
        fraction  = len(chunk) / total_chars if total_chars else 1 / len(chunks)
        chunk_dur = duration * fraction
        end       = cursor + chunk_dur if i < len(chunks) - 1 else seg["end"]
        result.append({"start": cursor, "end": end, "text": chunk})
        cursor = end
 
    return result
 
 
def apply_max_chars(segments: list, max_chars: int) -> list:
    """Expand every segment that exceeds max_chars into smaller sub-segments."""
    if not max_chars or max_chars <= 0:
        return segments
    out = []
    for seg in segments:
        out.extend(split_segment(seg, max_chars))
    return out
 
 
# ── timestamp / format helpers ────────────────────────────────────────────────
 
def format_timestamp(seconds: float, vtt: bool = False) -> str:
    """Convert seconds → HH:MM:SS,mmm  (or .mmm for VTT)."""
    millis = int(round(seconds * 1000))
    h      = millis // 3_600_000;  millis %= 3_600_000
    m      = millis // 60_000;     millis %= 60_000
    s      = millis // 1_000;      ms = millis % 1_000
    sep    = "." if vtt else ","
    return f"{h:02d}:{m:02d}:{s:02d}{sep}{ms:03d}"
 
 
def segments_to_srt(segments: list) -> str:
    lines = []
    for i, seg in enumerate(segments, start=1):
        lines.append(
            f"{i}\n"
            f"{format_timestamp(seg['start'])} --> {format_timestamp(seg['end'])}\n"
            f"{seg['text'].strip()}\n"
        )
    return "\n".join(lines)
 
 
def segments_to_vtt(segments: list) -> str:
    lines = ["WEBVTT\n"]
    for seg in segments:
        lines.append(
            f"{format_timestamp(seg['start'], vtt=True)} --> "
            f"{format_timestamp(seg['end'], vtt=True)}\n"
            f"{seg['text'].strip()}\n"
        )
    return "\n".join(lines)
 
 
def segments_to_txt(segments: list) -> str:
    return "\n".join(seg["text"].strip() for seg in segments)
 