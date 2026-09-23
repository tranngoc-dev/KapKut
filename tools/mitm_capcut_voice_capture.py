#!/usr/bin/env python3
"""
mitmproxy addon: capture CapCut effect/voice list API responses.

Usage:
  mitmdump -s tools/mitm_capcut_voice_capture.py -p 8080

Then set system / CapCut proxy to 127.0.0.1:8080 (and trust mitmproxy CA if needed).
In CapCut PC: open Text-to-speech / voice panel and scroll all languages.
"""

from __future__ import annotations

import json
import re
import time
from pathlib import Path

from mitmproxy import http

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT
URL_HINTS = (
    "effect",
    "voice",
    "tone",
    "timbre",
    "text_to_speech",
    "tts",
    "panel",
    "artist",
    "vimo",
    "lv/v1",
    "media_api",
)


def looks_like_voice_payload(text: str) -> bool:
    if "effect_item_list" in text:
        return True
    if "voice_type" in text and ("resource_id" in text or "effect_id" in text or "tonetype" in text):
        return True
    if '"timbre"' in text and "effect" in text:
        return True
    return False


class CapCutVoiceCapture:
    def response(self, flow: http.HTTPFlow) -> None:
        if flow.response is None:
            return
        url = flow.request.pretty_url
        host = flow.request.pretty_host or ""
        # CapCut / ByteDance hosts
        if not any(h in host for h in ("capcut", "byteoversea", "bytedance", "tiktok", "ibytedtos", "capcutapi", "jianying")):
            # still allow if path strongly matches
            if not any(k in url.lower() for k in URL_HINTS):
                return

        try:
            content = flow.response.get_text(strict=False) or ""
        except Exception:
            return
        if not content or len(content) < 200:
            return
        if not looks_like_voice_payload(content):
            return

        ts = int(time.time())
        out = OUT_DIR / f"captured_voices_{ts}.json"
        # avoid stampede same second
        i = 0
        while out.exists():
            i += 1
            out = OUT_DIR / f"captured_voices_{ts}_{i}.json"

        # Prefer pretty JSON if valid
        try:
            data = json.loads(content)
            out.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        except Exception:
            out.write_text(content, encoding="utf-8", errors="replace")

        n_items = 0
        try:
            items = data.get("data", {}).get("effect_item_list") or []
            n_items = len(items)
        except Exception:
            pass

        print(f"[voice-capture] saved {out.name} from {host}{flow.request.path[:80]} items~{n_items} bytes={len(content)}")


addons = [CapCutVoiceCapture()]
