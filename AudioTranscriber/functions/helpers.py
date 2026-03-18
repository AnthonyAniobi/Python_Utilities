def format_timestamp(seconds: float) -> str:
    """Convert seconds to SRT timestamp  HH:MM:SS,mmm"""
    millis = int(round(seconds * 1000))
    h = millis // 3_600_000
    millis %= 3_600_000
    m = millis // 60_000
    millis %= 60_000
    s = millis // 1_000
    ms = millis % 1_000
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"
 
 
def segments_to_srt(segments) -> str:
    lines = []
    for i, seg in enumerate(segments, start=1):
        start = format_timestamp(seg["start"])
        end   = format_timestamp(seg["end"])
        text  = seg["text"].strip()
        lines.append(f"{i}\n{start} --> {end}\n{text}\n")
    return "\n".join(lines)
 
 
def segments_to_vtt(segments) -> str:
    lines = ["WEBVTT\n"]
    for seg in segments:
        start = format_timestamp(seg["start"]).replace(",", ".")
        end   = format_timestamp(seg["end"]).replace(",", ".")
        text  = seg["text"].strip()
        lines.append(f"{start} --> {end}\n{text}\n")
    return "\n".join(lines)
 
 
def segments_to_txt(segments) -> str:
    return "\n".join(seg["text"].strip() for seg in segments)
 