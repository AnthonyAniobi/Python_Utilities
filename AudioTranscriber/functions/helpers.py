import os
import json
 
 
# ── word-level segment flattening ────────────────────────────────────────────
 
def flatten_to_words(segments: list) -> list:
    """
    Extract a flat list of word dicts from whisper-timestamped segments.
 
    whisper-timestamped stores words under seg["words"] as:
        {"text": "hello", "start": 0.0, "end": 0.4, "confidence": 0.99}
 
    openai-whisper (fallback) uses:
        {"word": "hello", "start": 0.0, "end": 0.4}
 
    We normalise both into {"word": str, "start": float, "end": float}.
    """
    words = []
    for seg in segments:
        seg_words = seg.get("words", [])
        if seg_words:
            for w in seg_words:
                # whisper-timestamped uses "text"; openai-whisper uses "word"
                text = (w.get("text") or w.get("word") or "").strip()
                if not text:
                    continue
                words.append({
                    "word":  text,
                    "start": float(w.get("start", seg["start"])),
                    "end":   float(w.get("end",   seg["end"])),
                })
        else:
            # No per-word timestamps — treat whole segment as one token
            words.append({
                "word":  seg["text"].strip(),
                "start": seg["start"],
                "end":   seg["end"],
            })
    return [w for w in words if w["word"]]
 
 
def groups_to_segments(word_groups: list) -> list:
    """
    Convert a list of word-groups (each a list of word dicts) into
    caption segments with accurate start/end times taken directly
    from the first and last word in each group.
    """
    result = []
    for group in word_groups:
        if not group:
            continue
        result.append({
            "start": group[0]["start"],
            "end":   group[-1]["end"],
            "text":  " ".join(w["word"] for w in group),
        })
    return result
 
 
# ── caption splitting: max characters ────────────────────────────────────────
 
def apply_max_chars(segments: list, max_chars: int) -> list:
    """
    Re-group word-level tokens so no caption exceeds max_chars.
    Picks the word boundary closest to the limit (may go slightly over
    or under) — words are never split.
    Uses precise per-word timestamps so timing is always accurate.
    """
    if not max_chars or max_chars <= 0:
        return segments
 
    words = flatten_to_words(segments)
    if not words:
        return segments
 
    groups, current, current_len = [], [], 0
 
    for w in words:
        wlen    = len(w["word"])
        new_len = current_len + (1 if current else 0) + wlen
 
        if not current:
            current.append(w)
            current_len = wlen
        elif new_len <= max_chars:
            current.append(w)
            current_len = new_len
        else:
            overshoot  = new_len     - max_chars
            undershoot = max_chars   - current_len
            if overshoot <= undershoot:
                # Including the word is closer — add it and flush
                current.append(w)
                groups.append(current)
                current, current_len = [], 0
            else:
                # Stopping here is closer — flush, start new group
                groups.append(current)
                current, current_len = [w], wlen
 
    if current:
        groups.append(current)
 
    return groups_to_segments(groups)
 
 
# ── caption splitting: max duration ──────────────────────────────────────────
 
def apply_max_duration(segments: list, max_dur: float) -> list:
    """
    Re-group word-level tokens so no caption exceeds max_dur seconds.
    Splits at the word boundary whose midpoint is closest to each
    max_dur boundary — words are never cut.
    Uses precise per-word timestamps so timing is always accurate.
    """
    if not max_dur or max_dur <= 0:
        return segments
 
    words = flatten_to_words(segments)
    if not words:
        return segments
 
    groups, current = [], []
    group_start = words[0]["start"] if words else 0.0
 
    for w in words:
        if not current:
            current.append(w)
            group_start = w["start"]
        else:
            duration_with    = w["end"]   - group_start
            duration_without = current[-1]["end"] - group_start
 
            if duration_without <= max_dur:
                # Haven't hit the limit yet — keep adding
                current.append(w)
            else:
                # Already over — flush and start new group with this word
                groups.append(current)
                current    = [w]
                group_start = w["start"]
 
    if current:
        groups.append(current)
 
    return groups_to_segments(groups)
 
 
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
 