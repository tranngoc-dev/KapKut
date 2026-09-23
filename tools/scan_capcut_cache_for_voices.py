#!/usr/bin/env python3
"""Scan CapCut User Data for cached effect/voice list payloads and dump matches."""

from __future__ import annotations

import json
import os
import re
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CACHE_ROOT = Path(os.environ.get("LOCALAPPDATA", "")) / "CapCut" / "User Data"
OUT_DIR = ROOT

PAT = re.compile(rb"effect_item_list|voice_type|tonetype|category_resources")
SKIP_DIR = {
    "videos",
    "ae-model",
    "models",
    "logs",
    "crashpad",
    "gpuCache",
    "ShaderCache",
    "GrShaderCache",
    "Code Cache",
}


def try_extract_json_blobs(data: bytes) -> list[dict]:
    """Best-effort extract JSON objects containing effect_item_list from binary/text cache."""
    out: list[dict] = []
    text = None
    for enc in ("utf-8", "utf-16-le"):
        try:
            text = data.decode(enc)
            break
        except Exception:
            continue
    if text is None:
        # still try utf-8 replace for ascii-ish json islands
        text = data.decode("utf-8", errors="ignore")

    # whole-file JSON
    s = text.strip()
    if s.startswith("{") or s.startswith("["):
        try:
            obj = json.loads(s)
            if isinstance(obj, (dict, list)):
                out.append(obj if isinstance(obj, dict) else {"data": obj})
                return out
        except Exception:
            pass

    # find effect_item_list islands and expand braces outward
    for m in re.finditer(r"effect_item_list", text):
        i = m.start()
        # walk back to nearest {
        start = text.rfind("{", 0, i)
        if start < 0:
            continue
        # crude brace match limited window
        depth = 0
        end = None
        for j in range(start, min(len(text), start + 8_000_000)):
            ch = text[j]
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    end = j + 1
                    break
        if end is None:
            continue
        chunk = text[start:end]
        try:
            obj = json.loads(chunk)
            if isinstance(obj, dict):
                out.append(obj)
        except Exception:
            continue
    return out


def main() -> None:
    if not CACHE_ROOT.exists():
        raise SystemExit(f"CapCut User Data not found: {CACHE_ROOT}")

    hits: list[tuple[str, int]] = []
    saved = 0
    ts = int(time.time())

    for dirpath, dirnames, filenames in os.walk(CACHE_ROOT):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIR and not d.startswith(".")]
        for fn in filenames:
            p = Path(dirpath) / fn
            try:
                sz = p.stat().st_size
            except OSError:
                continue
            if sz < 1500 or sz > 30_000_000:
                continue
            if p.suffix.lower() in {
                ".mp4",
                ".mp3",
                ".m4a",
                ".png",
                ".jpg",
                ".jpeg",
                ".webp",
                ".gif",
                ".zip",
                ".pak",
                ".dll",
                ".exe",
                ".bin",
                ".wasm",
                ".ttf",
                ".otf",
            }:
                continue
            try:
                with p.open("rb") as fp:
                    chunk = fp.read(min(sz, 4_000_000))
            except OSError:
                continue
            if not PAT.search(chunk):
                continue
            # read full if partial matched and file not huge
            if sz > len(chunk) and sz <= 20_000_000:
                try:
                    chunk = p.read_bytes()
                except OSError:
                    pass
            hits.append((str(p), sz))
            blobs = try_extract_json_blobs(chunk)
            for bi, blob in enumerate(blobs):
                # must look like voice payload
                dump = json.dumps(blob, ensure_ascii=False)
                if "effect_item_list" not in dump and "voice_type" not in dump:
                    continue
                out = OUT_DIR / f"captured_voices_cache_{ts}_{saved}.json"
                # wrap if needed
                if "ret" not in blob and "data" not in blob:
                    payload = {"ret": "0", "errmsg": "from_cache", "data": blob}
                elif "data" not in blob and "effect_item_list" in blob:
                    payload = {"ret": "0", "errmsg": "from_cache", "data": blob}
                else:
                    payload = blob
                out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
                saved += 1
                print(f"[saved] {out.name} from {p} ({sz} bytes)")

    print(f"hits_files={len(hits)} saved_json={saved}")
    for path, sz in hits[:30]:
        print(f"  {sz:10d}  {path}")


if __name__ == "__main__":
    main()
