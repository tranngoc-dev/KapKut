#!/usr/bin/env python3
"""Script → multi-scene TTS helpers: parse, smart split, SRT offset/merge."""

from __future__ import annotations

import re
from typing import Any


SCENE_SEP_RE = re.compile(r"(?m)^\s*(?:---+|===+)\s*$")
HEADING_RE = re.compile(r"(?m)^(#{1,3})\s+(.+)$")
SENTENCE_END_RE = re.compile(r"(?<=[.!?…。！？])\s+|(?<=\n)")


def normalize_newlines(text: str) -> str:
    return (text or "").replace("\r\n", "\n").replace("\r", "\n").strip()


def parse_script_scenes(script: str, mode: str = "auto") -> list[dict[str, Any]]:
    """
    Parse a script into scenes.

    mode:
      - auto: --- / === separators, else markdown headings, else blank-line paragraphs
      - separator: only --- / ===
      - heading: markdown # headings
      - paragraph: blank-line paragraphs
      - single: whole script as one scene
    """
    text = normalize_newlines(script)
    if not text:
        return []

    mode = (mode or "auto").lower()
    if mode == "single":
        return [{"index": 1, "title": "Scene 1", "text": text}]

    if mode == "auto":
        if SCENE_SEP_RE.search(text):
            mode = "separator"
        elif HEADING_RE.search(text):
            mode = "heading"
        else:
            mode = "paragraph"

    scenes: list[dict[str, Any]] = []

    if mode == "separator":
        parts = SCENE_SEP_RE.split(text)
        for i, part in enumerate(parts, 1):
            part = part.strip()
            if not part:
                continue
            title, body = _split_title_body(part, fallback=f"Scene {i}")
            scenes.append({"index": len(scenes) + 1, "title": title, "text": body})
    elif mode == "heading":
        matches = list(HEADING_RE.finditer(text))
        if not matches:
            scenes.append({"index": 1, "title": "Scene 1", "text": text})
        else:
            # preamble before first heading
            pre = text[: matches[0].start()].strip()
            if pre:
                scenes.append({"index": 1, "title": "Mở đầu", "text": pre})
            for i, m in enumerate(matches):
                title = m.group(2).strip() or f"Scene {i + 1}"
                start = m.end()
                end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
                body = text[start:end].strip()
                if not body:
                    continue
                scenes.append({"index": len(scenes) + 1, "title": title, "text": body})
    else:  # paragraph
        parts = re.split(r"\n\s*\n+", text)
        for i, part in enumerate(parts, 1):
            part = part.strip()
            if not part:
                continue
            title, body = _split_title_body(part, fallback=f"Scene {i}")
            scenes.append({"index": len(scenes) + 1, "title": title, "text": body})

    # reindex
    for i, sc in enumerate(scenes, 1):
        sc["index"] = i
    return scenes


def _split_title_body(block: str, fallback: str) -> tuple[str, str]:
    lines = block.split("\n")
    first = lines[0].strip()
    # Title line patterns: "# Title", "Scene 1:", "[Title]", "1. Title"
    if first.startswith("#"):
        title = first.lstrip("#").strip() or fallback
        body = "\n".join(lines[1:]).strip() or first
        return title, body
    m = re.match(r"^(?:scene\s*\d+|cảnh\s*\d+)\s*[:.\-–—]\s*(.+)$", first, re.I)
    if m:
        title = m.group(1).strip() or first
        body = "\n".join(lines[1:]).strip() or "\n".join(lines).strip()
        return title, body
    if re.match(r"^\[\s*.+\s*\]$", first) and len(lines) > 1:
        title = first.strip("[] ").strip()
        body = "\n".join(lines[1:]).strip()
        return title, body
    # short first line as title if rest exists
    if len(lines) > 1 and len(first) <= 60 and not first.endswith((".", "!", "?", "。")):
        return first, "\n".join(lines[1:]).strip()
    return fallback, block.strip()


def smart_split_text(text: str, max_chars: int = 400) -> list[str]:
    """Split long text into TTS-safe chunks at sentence boundaries when possible."""
    text = normalize_newlines(text)
    if not text:
        return []
    max_chars = max(80, int(max_chars or 400))
    if len(text) <= max_chars:
        return [text]

    # First split into sentences / fragments
    pieces: list[str] = []
    buf = text
    while buf:
        if len(buf) <= max_chars:
            pieces.append(buf.strip())
            break
        window = buf[: max_chars + 1]
        # prefer last sentence end in window
        cut = -1
        for m in re.finditer(r"[.!?…。！？](?:\s+|$)|[\n]", window):
            cut = m.end()
        if cut < max(40, max_chars // 4):
            # fallback: last space
            sp = window.rfind(" ")
            cut = sp if sp > max(20, max_chars // 5) else max_chars
        chunk = buf[:cut].strip()
        if not chunk:
            chunk = buf[:max_chars].strip()
            cut = max_chars
        pieces.append(chunk)
        buf = buf[cut:].lstrip()

    return [p for p in pieces if p]


def expand_scenes_with_splits(
    scenes: list[dict[str, Any]], max_chars: int = 400
) -> list[dict[str, Any]]:
    """Expand scenes into TTS segments (scene may become multiple segments)."""
    segments: list[dict[str, Any]] = []
    for sc in scenes:
        chunks = smart_split_text(sc.get("text") or "", max_chars=max_chars)
        if not chunks:
            continue
        for j, chunk in enumerate(chunks, 1):
            seg_title = sc.get("title") or f"Scene {sc.get('index', 1)}"
            if len(chunks) > 1:
                seg_title = f"{seg_title} ({j}/{len(chunks)})"
            segments.append(
                {
                    "index": len(segments) + 1,
                    "scene_index": sc.get("index"),
                    "title": seg_title,
                    "text": chunk,
                    "char_count": len(chunk),
                }
            )
    return segments


def srt_timestamp(seconds: float) -> str:
    if seconds < 0:
        seconds = 0.0
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int(round((seconds - int(seconds)) * 1000))
    if ms >= 1000:
        s += 1
        ms -= 1000
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def clock_timestamp(seconds: float, sep: str = ".") -> str:
    """HH:MM:SS.mmm (or with custom ms separator)."""
    if seconds < 0:
        seconds = 0.0
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int(round((seconds - int(seconds)) * 1000))
    if ms >= 1000:
        s += 1
        ms -= 1000
    return f"{h:02d}:{m:02d}:{s:02d}{sep}{ms:03d}"


def _ms_to_seconds(value) -> float:
    """CapCut usually returns ms; tolerate seconds if value is small float."""
    if value is None:
        return 0.0
    try:
        v = float(value)
    except (TypeError, ValueError):
        return 0.0
    # Heuristic: values under 1e5 might still be ms for short clips;
    # CapCut utterance times are almost always milliseconds.
    return v / 1000.0


def _to_ms(value) -> int:
    return int(round(_ms_to_seconds(value) * 1000))


_SENTENCE_END_RE = re.compile(r'[.!?…。！？]+["\'”’)\]]*\s*$')


def normalize_utterances(capcut_json) -> list[dict]:
    """Flatten CapCut utterances to {start_ms, end_ms, text}, drop empty."""
    raw = (capcut_json or {}).get("utterances") or []
    out: list[dict] = []
    for utt in raw:
        text = re.sub(r"\s+", " ", str(utt.get("text") or "").strip())
        if not text:
            continue
        start_ms = _to_ms(utt.get("start_time", 0))
        end_ms = _to_ms(utt.get("end_time", utt.get("start_time", 0)))
        if end_ms <= start_ms:
            end_ms = start_ms + 300
        out.append({"start_ms": start_ms, "end_ms": end_ms, "text": text})
    return out


def _ends_complete_sentence(text: str) -> bool:
    return bool(_SENTENCE_END_RE.search((text or "").strip()))


def merge_utterances(
    utterances: list[dict],
    enabled: bool = True,
    max_gap_ms: int = 450,
    max_chars: int = 100,
    max_duration_ms: int = 6000,
) -> list[dict]:
    """
    Merge short CapCut cues into longer sentence-like segments.

    Example:
      "em chỗ mua cái" (0.94→1.54) + "váy này" (1.54→3.10)
      → "em chỗ mua cái váy này" (0.94→3.10)

    Rules (when enabled):
      - merge if gap between cues <= max_gap_ms
      - and previous text does NOT already end with sentence punctuation
      - and merged text length <= max_chars
      - and merged duration <= max_duration_ms
    """
    if not enabled or not utterances:
        return list(utterances or [])

    max_gap_ms = max(0, int(max_gap_ms))
    max_chars = max(20, int(max_chars))
    max_duration_ms = max(500, int(max_duration_ms))

    merged: list[dict] = []
    for utt in utterances:
        if not merged:
            merged.append(dict(utt))
            continue

        prev = merged[-1]
        gap = int(utt["start_ms"]) - int(prev["end_ms"])
        combined_text = f"{prev['text']} {utt['text']}".strip()
        combined_dur = int(utt["end_ms"]) - int(prev["start_ms"])

        can_merge = (
            gap <= max_gap_ms
            and not _ends_complete_sentence(prev["text"])
            and len(combined_text) <= max_chars
            and combined_dur <= max_duration_ms
        )
        # Always allow merge of very short tails (e.g. 1–3 words) when gap is tiny
        if not can_merge and gap <= max_gap_ms and not _ends_complete_sentence(prev["text"]):
            word_count = len(utt["text"].split())
            if word_count <= 3 and combined_dur <= max_duration_ms and len(combined_text) <= max_chars + 40:
                can_merge = True

        if can_merge:
            prev["text"] = combined_text
            prev["end_ms"] = int(utt["end_ms"])
            prev["merged_from"] = int(prev.get("merged_from") or 1) + 1
        else:
            merged.append(dict(utt))

    return merged


def utterances_to_timestamped_txt(
    capcut_json,
    style: str = "start",
    merge: bool = True,
    max_gap_ms: int = 450,
    max_chars: int = 100,
    max_duration_ms: int = 6000,
):
    """
    Build plain-text transcript with timestamp at the start of each utterance/sentence.

    style:
      - start:     [00:00:01.234] sentence
      - range:     [00:00:01.234 → 00:00:03.500] sentence
      - plain:     00:00:01.234 sentence
      - srt_line:  00:00:00,220 --> 00:00:00,940 sentence   (1 line, SRT clocks)
      - srt_block: full SRT blocks (index + times + text), empty cues skipped
    """
    normalized = normalize_utterances(capcut_json)
    segments = merge_utterances(
        normalized,
        enabled=merge,
        max_gap_ms=max_gap_ms,
        max_chars=max_chars,
        max_duration_ms=max_duration_ms,
    )

    lines_out: list[str] = []
    rows: list[dict] = []
    style = (style or "start").lower()
    cue_idx = 0

    for seg in segments:
        text = seg["text"]
        start_s = seg["start_ms"] / 1000.0
        end_s = seg["end_ms"] / 1000.0

        start_dot = clock_timestamp(start_s, ".")
        end_dot = clock_timestamp(end_s, ".")
        start_srt = srt_timestamp(start_s)
        end_srt = srt_timestamp(end_s)
        cue_idx += 1

        if style == "range":
            line = f"[{start_dot} → {end_dot}] {text}"
        elif style == "plain":
            line = f"{start_dot} {text}"
        elif style == "srt_line":
            line = f"{start_srt} --> {end_srt} {text}"
        elif style == "srt_block":
            line = f"{cue_idx}\n{start_srt} --> {end_srt}\n{text}\n"
        elif style in ("no_timestamp", "none", "text_only", "no_ts", "raw"):
            line = text
        else:
            line = f"[{start_dot}] {text}"

        lines_out.append(line)
        rows.append(
            {
                "index": cue_idx,
                "start_ms": seg["start_ms"],
                "end_ms": seg["end_ms"],
                "start": start_srt if style in ("srt_line", "srt_block") else start_dot,
                "end": end_srt if style in ("srt_line", "srt_block") else end_dot,
                "text": text,
                "merged_from": seg.get("merged_from") or 1,
                "line": line if style != "srt_block" else f"{start_srt} --> {end_srt} {text}",
            }
        )

    if style == "srt_block":
        body = "\n".join(lines_out)
        if body and not body.endswith("\n"):
            body += "\n"
    else:
        body = "\n".join(lines_out)
        if body:
            body += "\n"
    return body, rows


def utterances_to_srt_string(
    capcut_json,
    merge: bool = True,
    max_gap_ms: int = 450,
    max_chars: int = 100,
    max_duration_ms: int = 6000,
) -> str:
    """SRT from utterances with optional short-cue merge (same rules as TXT)."""
    normalized = normalize_utterances(capcut_json)
    segments = merge_utterances(
        normalized,
        enabled=merge,
        max_gap_ms=max_gap_ms,
        max_chars=max_chars,
        max_duration_ms=max_duration_ms,
    )
    blocks = []
    for i, seg in enumerate(segments, 1):
        start = seg["start_ms"] / 1000.0
        end = seg["end_ms"] / 1000.0
        blocks.append(
            f"{i}\n{srt_timestamp(start)} --> {srt_timestamp(end)}\n{seg['text']}\n"
        )
    return "\n".join(blocks)


def simple_srt_for_segment(text: str, duration_ms: int, start_offset_ms: int = 0) -> str:
    """One-cue SRT covering the whole segment (no word-level timing)."""
    start = start_offset_ms / 1000.0
    end = (start_offset_ms + max(duration_ms, 500)) / 1000.0
    body = re.sub(r"\s+", " ", (text or "").strip())
    return f"1\n{srt_timestamp(start)} --> {srt_timestamp(end)}\n{body}\n"


def offset_srt_content(srt_text: str, offset_ms: int, start_index: int = 1) -> tuple[str, int]:
    """Shift all cues in an SRT by offset_ms. Returns (new_srt, next_index)."""
    if not (srt_text or "").strip():
        return "", start_index

    cue_re = re.compile(
        r"(?m)^(\d+)\s*\n"
        r"(\d{2}:\d{2}:\d{2}[,.]\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2}[,.]\d{3})\s*\n"
        r"([\s\S]*?)(?=\n\d+\s*\n\d{2}:\d{2}:\d{2}|\Z)"
    )

    def parse_ts(ts: str) -> float:
        ts = ts.replace(".", ",")
        h, m, rest = ts.split(":")
        s, ms = rest.split(",")
        return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000.0

    def fmt(sec: float) -> str:
        return srt_timestamp(sec + offset_ms / 1000.0)

    blocks = []
    idx = start_index
    for m in cue_re.finditer(srt_text.strip() + "\n"):
        start_ts, end_ts, body = m.group(2), m.group(3), m.group(4).strip()
        blocks.append(
            f"{idx}\n{fmt(parse_ts(start_ts))} --> {fmt(parse_ts(end_ts))}\n{body}\n"
        )
        idx += 1

    if not blocks:
        # fallback: treat whole as one cue already formatted poorly
        return srt_text, start_index
    return "\n".join(blocks) + "\n", idx


def merge_srt_files(segment_srts: list[tuple[str, int]]) -> str:
    """
    Merge list of (srt_text, start_offset_ms).
    Each srt_text should be relative to 0 for its own segment OR already absolute.
    We assume each srt is relative (starts near 0) and apply offset.
    """
    parts = []
    next_idx = 1
    for srt_text, offset_ms in segment_srts:
        shifted, next_idx = offset_srt_content(srt_text, offset_ms, next_idx)
        if shifted.strip():
            parts.append(shifted.strip())
    return "\n\n".join(parts) + ("\n" if parts else "")


def sanitize_filename(name: str, max_len: int = 60) -> str:
    name = re.sub(r'[\\/:*?"<>|]+', "", name or "")
    name = re.sub(r"\s+", "_", name.strip())
    name = name.strip("._") or "segment"
    return name[:max_len]
