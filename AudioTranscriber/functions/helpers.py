import os
import json
 
 
# ── caption splitting: max characters ────────────────────────────────────────
 
def split_text_to_chunks(text: str, max_chars: int) -> list:
    """
    Split text into chunks guided by max_chars without ever cutting a word.
    Picks whichever word boundary lands closest to the target — so chunks
    may be slightly above or below max_chars, but no word is ever split.
    """
    words = text.split()
    if not words:
        return []
 
    chunks, current_words, current_len = [], [], 0
 
    for word in words:
        word_len = len(word)
        new_len  = current_len + (1 if current_words else 0) + word_len
 
        if not current_words:
            current_words.append(word)
            current_len = word_len
        elif new_len <= max_chars:
            current_words.append(word)
            current_len = new_len
        else:
            overshoot  = new_len      - max_chars
            undershoot = max_chars    - current_len
            if overshoot <= undershoot:
                current_words.append(word)
                chunks.append(" ".join(current_words))
                current_words, current_len = [], 0
            else:
                chunks.append(" ".join(current_words))
                current_words, current_len = [word], word_len
 
    if current_words:
        chunks.append(" ".join(current_words))
    return chunks
 
 
def split_segment_by_chars(seg: dict, max_chars: int) -> list:
    text = seg["text"].strip()
    if len(text) <= max_chars:
        return [seg]
    chunks = split_text_to_chunks(text, max_chars)
    if len(chunks) <= 1:
        return [seg]
    total_chars = sum(len(c) for c in chunks)
    duration    = seg["end"] - seg["start"]
    result, cursor = [], seg["start"]
    for i, chunk in enumerate(chunks):
        frac = len(chunk) / total_chars if total_chars else 1 / len(chunks)
        end  = cursor + duration * frac if i < len(chunks) - 1 else seg["end"]
        result.append({"start": cursor, "end": end, "text": chunk})
        cursor = end
    return result
 
 
def apply_max_chars(segments: list, max_chars: int) -> list:
    if not max_chars or max_chars <= 0:
        return segments
    out = []
    for seg in segments:
        out.extend(split_segment_by_chars(seg, max_chars))
    return out
 
 
# ── caption splitting: max duration ──────────────────────────────────────────
 
def split_segment_by_duration(seg: dict, max_dur: float) -> list:
    """
    Split a segment whose duration exceeds max_dur into sub-segments.
    Text is divided proportionally by word count; each sub-segment gets
    an equal share of the words and a proportional slice of the time.
    Words are never cut — the duration limit is a soft guide just like
    the character limit.
    """
    duration = seg["end"] - seg["start"]
    if duration <= max_dur:
        return [seg]
 
    words = seg["text"].strip().split()
    if not words:
        return [seg]
 
    # How many sub-segments do we need?
    n_parts = max(2, round(duration / max_dur))
 
    # Distribute words as evenly as possible
    base, extra = divmod(len(words), n_parts)
    word_groups = []
    idx = 0
    for i in range(n_parts):
        size = base + (1 if i < extra else 0)
        word_groups.append(words[idx: idx + size])
        idx += size
 
    # Remove any empty groups (can happen if word count < n_parts)
    word_groups = [g for g in word_groups if g]
 
    total_words = len(words)
    result, cursor = [], seg["start"]
    for i, group in enumerate(word_groups):
        frac = len(group) / total_words if total_words else 1 / len(word_groups)
        end  = cursor + duration * frac if i < len(word_groups) - 1 else seg["end"]
        result.append({"start": cursor, "end": end, "text": " ".join(group)})
        cursor = end
    return result
 
 
def apply_max_duration(segments: list, max_dur: float) -> list:
    if not max_dur or max_dur <= 0:
        return segments
    out = []
    for seg in segments:
        out.extend(split_segment_by_duration(seg, max_dur))
    return out
 
 
# ── timestamp / format helpers ────────────────────────────────────────────────
 
def format_timestamp(seconds: float, vtt: bool = False) -> str:
    millis = int(round(seconds * 1000))
    h      = millis // 3_600_000;  millis %= 3_600_000
    m      = millis // 60_000;     millis %= 60_000
    s      = millis // 1_000;      ms = millis % 1_000
    sep    = "." if vtt else ","
    return f"{h:02d}:{m:02d}:{s:02d}{sep}{ms:03d}"
 
 
def seconds_to_ticks(seconds: float, ticks_per_second: int = 254016000000) -> int:
    """Convert seconds to Premiere Pro internal ticks (254,016,000,000 ticks/sec)."""
    return int(round(seconds * ticks_per_second))
 
 
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
 
 
def segments_to_premiere_json(segments: list, source_filename: str = "") -> str:
    """
    Build a Premiere Pro-compatible JSON caption file.
 
    The structure follows the format expected when you import a captions
    track via File > Import in Premiere Pro (JSON captions preset).
    Each caption carries:
      - startTime / endTime  in both seconds and Premiere ticks
      - text content
      - a sequential index
    """
    TICKS = 254_016_000_000  # Premiere Pro's ticks-per-second constant
 
    captions = []
    for i, seg in enumerate(segments):
        start_s = seg["start"]
        end_s   = seg["end"]
        captions.append({
            "index":          i,
            "startTime":      round(start_s, 6),
            "endTime":        round(end_s,   6),
            "startTimeTicks": seconds_to_ticks(start_s, TICKS),
            "endTimeTicks":   seconds_to_ticks(end_s,   TICKS),
            "lines": [seg["text"].strip()],
        })
 
    payload = {
        "version":        "1.0",
        "format":         "PremierePro-CaptionJSON",
        "sourceFile":     os.path.basename(source_filename),
        "totalCaptions":  len(captions),
        "captions":       captions,
    }
    return json.dumps(payload, indent=2, ensure_ascii=False)
 