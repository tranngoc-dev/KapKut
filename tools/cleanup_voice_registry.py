#!/usr/bin/env python3
"""Map languages + filter Voice.json to TTS-usable entries."""

from __future__ import annotations

import argparse
import json
import re
import shutil
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VOICE_FILE = ROOT / "Voice.json"

LANG_MAP = {
    "vi": "vi-VN",
    "en": "en-US",
    "zh": "zh-CN",
    "ja": "ja-JP",
    "jp": "ja-JP",
    "ko": "ko-KR",
    "kr": "ko-KR",
    "id": "id-ID",
    "th": "th-TH",
    "es": "es-ES",
    "mx": "es-MX",
    "pt": "pt-BR",
    "br": "pt-BR",
    "fr": "fr-FR",
    "de": "de-DE",
    "it": "it-IT",
    "ms": "ms-MY",
    "my": "ms-MY",
    "fil": "fil-PH",
    "hi": "hi-IN",
    "ar": "ar-SA",
    "ru": "ru-RU",
    "tr": "tr-TR",
    "nl": "nl-NL",
    "pl": "pl-PL",
    "sv": "sv-SE",
    "uk": "uk-UA",
    "ro": "ro-RO",
    "cs": "cs-CZ",
    "hu": "hu-HU",
    "el": "el-GR",
    "he": "he-IL",
    "bg": "bg-BG",
    "hr": "hr-HR",
    "sk": "sk-SK",
    "da": "da-DK",
    "fi": "fi-FI",
    "nb": "nb-NO",
    "no": "nb-NO",
    "yue": "zh-HK",
    "cantonese": "zh-HK",
}

# Display-name keyword → lang (order matters: more specific first)
NAME_HINTS = [
    (r"cantonese|quảng đông|粤语|廣東", "zh", "zh-HK"),
    (r"indonesian|indonesia|suara|bahasa", "id", "id-ID"),
    (r"malay|bahasa melayu|\bmy\b", "ms", "ms-MY"),
    (r"thai|tiếng thái", "th", "th-TH"),
    (r"portuguese|portugu|brasileir|masculino|homem|mulher", "pt", "pt-BR"),
    (r"spanish|español|hombre|mujer|seri[oa]", "es", "es-ES"),
    (r"french|français|francaise", "fr", "fr-FR"),
    (r"german|deutsch", "de", "de-DE"),
    (r"japanese|日本語|nihon", "ja", "ja-JP"),
    (r"korean|한국어|hangul", "ko", "ko-KR"),
    (r"chinese|mandarin|phổ thông|中文|普通话", "zh", "zh-CN"),
    (r"vietnamese|tiếng việt|việt", "vi", "vi-VN"),
    (r"english|american|british|uk\b|us\b", "en", "en-US"),
]

# Known BV codes from older curated registry (filled at runtime from non-und entries)
BV_CODE_RE = re.compile(r"^(BV\d+)", re.I)


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def guess_lang(voice_type: str, display_name: str = "") -> tuple[str, str]:
    vt = (voice_type or "").strip()
    vtl = vt.lower()
    name = display_name or ""

    # DiT_en_..., multi_zh_..., ICL_en_..., ICL_uranus_es_..., ICL_jp_..., ICL_mx_...
    patterns = [
        r"^(?:dit|icl|multi)_([a-z]{2,3})_",
        r"^icl_uranus_([a-z]{2,3})_",
        r"^(?:icl_)?([a-z]{2,3})_(?:male|female|kid|child)_",
        r"^([a-z]{2,3})_(?:male|female|us|uk|au|in)_",
        r"^([a-z]{2,3})_[a-z0-9]",
    ]
    for pat in patterns:
        m = re.match(pat, vtl)
        if m:
            code = m.group(1)
            if code in LANG_MAP:
                lan = "ja" if code == "jp" else ("ko" if code == "kr" else code)
                if lan == "jp":
                    lan = "ja"
                if lan == "kr":
                    lan = "ko"
                if lan == "yue":
                    lan = "zh"
                lang = LANG_MAP.get(code) or LANG_MAP.get(lan, "und")
                if lang != "und":
                    return lan if lan in LANG_MAP or lan in ("ja", "ko", "zh") else code, lang

    # multi_* without lang token → multilingual / often EN UI catalog
    if vtl.startswith("multi_"):
        return "multi", "multi"

    # display name hints
    nl = name.lower()
    for pat, lan, lang in NAME_HINTS:
        if re.search(pat, nl, re.I):
            return lan, lang

    # 11labs-style short alnum ids → usually EN catalog in CapCut overseas
    if re.fullmatch(r"[A-Za-z0-9]{16,28}", vt):
        return "en", "en-US"

    # ICL hash-only
    if re.fullmatch(r"ICL_[0-9a-f]{8,16}", vt, re.I):
        return "en", "en-US"

    return "und", "und"


def is_classic_tts_voice(voice_type: str) -> bool:
    """Keep voices that look like CapCut/SAMI TTS ids (not pure noise)."""
    vt = voice_type or ""
    if not vt or len(vt) < 3:
        return False
    # classic families
    if vt.startswith(("BV", "ICL_", "DiT_", "multi_")):
        return True
    if re.match(
        r"^(en|zh|vi|ja|jp|ko|kr|id|th|es|pt|fr|de|it|ms|my|hi|ar|ru|tr|nl|fil|yue|mx)_",
        vt,
        re.I,
    ):
        return True
    # Azure Neural / xx-YY-* platform ids — NOT accepted by CapCut sami_text_to_speech
    # (health-check: TTSInvalidSpeaker). Do not treat as classic TTS.
    if re.match(r"^[a-z]{2}-[A-Z]{2}-", vt) or "Neural" in vt:
        return False
    # 11labs-style alnum ids often appear in avatar panels but fail TTS on CapCut API.
    # Keep them only if caller explicitly wants (is_classic returns False here).
    if re.fullmatch(r"[A-Za-z0-9]{16,28}", vt):
        return False
    return False


def apply_bv_lang_from_known(voices: list[dict]) -> None:
    """If same BVxxx base code has a known lang elsewhere, copy it to und siblings."""
    known: dict[str, tuple[str, str]] = {}
    for v in voices:
        if v.get("lang") in (None, "", "und"):
            continue
        m = BV_CODE_RE.match(v.get("voice_type") or "")
        if m:
            known[m.group(1).upper()] = (v.get("lan") or "und", v["lang"])

    for v in voices:
        if v.get("lang") not in (None, "", "und"):
            continue
        m = BV_CODE_RE.match(v.get("voice_type") or "")
        if not m:
            continue
        hit = known.get(m.group(1).upper())
        if hit:
            v["lan"], v["lang"] = hit


def map_languages(voices: list[dict]) -> dict:
    stats = {"mapped": 0, "already": 0, "still_und": 0}
    for v in voices:
        if v.get("lang") and v["lang"] != "und":
            stats["already"] += 1
            continue
        lan, lang = guess_lang(v.get("voice_type") or "", v.get("display_name") or "")
        if lang != "und":
            v["lan"] = lan
            v["lang"] = lang
            stats["mapped"] += 1
        else:
            stats["still_und"] += 1
    apply_bv_lang_from_known(voices)
    # recount still_und after BV fill
    stats["still_und"] = sum(1 for v in voices if v.get("lang") in (None, "", "und"))
    return stats


def filter_voices(voices: list[dict], drop_und: bool, drop_alnum: bool) -> tuple[list[dict], dict]:
    kept = []
    removed = Counter()
    for v in voices:
        vt = v.get("voice_type") or ""
        if not v.get("resource_id"):
            removed["no_resource_id"] += 1
            continue
        if not is_classic_tts_voice(vt):
            removed["non_tts_shape"] += 1
            continue
        if drop_alnum and re.fullmatch(r"[A-Za-z0-9]{16,28}", vt):
            removed["alnum_id"] += 1
            continue
        if drop_und and v.get("lang") in (None, "", "und"):
            removed["und"] += 1
            continue
        # drop empty display that is useless? keep
        kept.append(v)

    # de-dupe by voice_type (keep first after sort for stability)
    by_type: dict[str, dict] = {}
    for v in sorted(
        kept,
        key=lambda x: (
            x.get("lang") or "",
            x.get("display_name") or "",
            x.get("voice_type") or "",
        ),
    ):
        by_type[v["voice_type"]] = v
    return list(by_type.values()), dict(removed)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--voice-file", default=str(VOICE_FILE))
    ap.add_argument("--drop-und", action="store_true", help="Remove lang=und after mapping")
    ap.add_argument(
        "--drop-alnum",
        action="store_true",
        help="Remove 11labs-style random alnum voice_type ids",
    )
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--no-backup", action="store_true")
    args = ap.parse_args()

    path = Path(args.voice_file)
    voices = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(voices, list):
        raise SystemExit("Voice.json must be array")

    before = len(voices)
    before_langs = Counter(v.get("lang") for v in voices)

    map_stats = map_languages(voices)
    after_map_langs = Counter(v.get("lang") for v in voices)

    filtered, removed = filter_voices(voices, drop_und=args.drop_und, drop_alnum=args.drop_alnum)
    filtered = sorted(
        filtered,
        key=lambda x: (x.get("lang") or "", x.get("display_name") or "", x.get("voice_type") or ""),
    )
    after_langs = Counter(v.get("lang") for v in filtered)

    print("=== map lang ===")
    print(map_stats)
    print("langs before:", before_langs.most_common(12))
    print("langs after map:", after_map_langs.most_common(12))
    print("=== filter ===")
    print(f"before={before} after={len(filtered)} removed={removed}")
    print("langs final:", after_langs.most_common(15))

    if args.dry_run:
        print("dry-run: not writing")
        return

    if not args.no_backup:
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        bak = path.with_suffix(f".bak_{stamp}.json")
        shutil.copy2(path, bak)
        print(f"backup: {bak.name}")

    path.write_text(json.dumps(filtered, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {path} ({len(filtered)} voices)")


if __name__ == "__main__":
    main()
