#!/usr/bin/env python3
"""Extract CapCut TTS voices from captured effect-list JSON responses and merge into Voice.json."""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_VOICE_FILE = ROOT / "Voice.json"


LANG_MAP = {
    "vi": "vi-VN",
    "en": "en-US",
    "zh": "zh-CN",
    "ja": "ja-JP",
    "ko": "ko-KR",
    "id": "id-ID",
    "th": "th-TH",
    "es": "es-ES",
    "pt": "pt-BR",
    "fr": "fr-FR",
    "de": "de-DE",
    "it": "it-IT",
    "ms": "ms-MY",
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
    "my": "my-MM",
    "km": "km-KH",
    "lo": "lo-LA",
    "bn": "bn-BD",
    "ta": "ta-IN",
    "te": "te-IN",
    "mr": "mr-IN",
    "gu": "gu-IN",
    "kn": "kn-IN",
    "ml": "ml-IN",
    "ur": "ur-PK",
    "fa": "fa-IR",
    "multi": "multi",
}


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def parse_maybe_json(value: Any) -> Any:
    if not isinstance(value, str):
        return value
    text = value.strip()
    if not text or text[0] not in "{[":
        return value
    try:
        return json.loads(text)
    except Exception:
        return value


def guess_lang_from_voice_type(voice_type: str) -> tuple[str, str]:
    vt = (voice_type or "").lower()
    # patterns: en_male_..., zh_female_..., BV074..., multi_zh_..., ICL_es_male_...
    m = re.match(r"^(?:icl_)?([a-z]{2,3})[_-]", vt)
    if m:
        lan = m.group(1)
        if lan in LANG_MAP:
            return lan, LANG_MAP[lan]
    m = re.match(r"^multi_([a-z]{2,3})_", vt)
    if m:
        lan = m.group(1)
        if lan in LANG_MAP:
            return lan, LANG_MAP[lan]
    # BV series defaults often VN/ID/CN depending on catalog; leave unknown
    if vt.startswith("bv"):
        return "und", "und"
    if vt.startswith("en_") or "_en_" in vt:
        return "en", "en-US"
    if vt.startswith("zh_") or "_zh_" in vt:
        return "zh", "zh-CN"
    return "und", "und"


def extract_voice_type(item: dict) -> str | None:
    # digital_human panel (AI avatar / character voices)
    dh = item.get("digital_human")
    if isinstance(dh, dict):
        vt = (dh.get("voice_type") or dh.get("low_version_voice_type") or "").strip()
        if vt:
            return vt

    # Prefer nested tonetype in extra / biz_extra
    for key in ("extra", "biz_extra", "common_attr"):
        blob = item.get(key)
        if key == "common_attr" and isinstance(blob, dict):
            blob = blob.get("extra") or blob.get("biz_extra")
        parsed = parse_maybe_json(blob)
        if isinstance(parsed, dict):
            tonetype = parse_maybe_json(parsed.get("tonetype"))
            if isinstance(tonetype, dict):
                vt = tonetype.get("voice_type") or tonetype.get("tts_voice")
                if vt:
                    return str(vt).strip()
            # sometimes flat
            vt = parsed.get("voice_type")
            if vt:
                return str(vt).strip()

    timbre = item.get("timbre") or {}
    if isinstance(timbre, dict):
        vt = (timbre.get("voice_type") or timbre.get("voice") or "").strip()
        if vt:
            return vt
    return None


def extract_resource_id(item: dict, voice_type: str) -> str | None:
    # Prefer dedicated voice resource id when present (digital_human / TTS)
    dh = item.get("digital_human")
    if isinstance(dh, dict):
        for key in ("voice_resource_id", "resource_id"):
            val = dh.get(key)
            if val is not None and str(val).strip() and str(val).strip() not in ("0", ""):
                return str(val).strip()

    for key in ("extra", "biz_extra"):
        parsed = parse_maybe_json(item.get(key))
        if isinstance(parsed, dict):
            for rk in ("resource_id", "voice_resource_id", "tone_resource_id"):
                val = parsed.get(rk)
                if val is not None and str(val).strip():
                    return str(val).strip()
            tonetype = parse_maybe_json(parsed.get("tonetype"))
            if isinstance(tonetype, dict):
                val = tonetype.get("resource_id")
                if val is not None and str(val).strip():
                    return str(val).strip()

    ca = item.get("common_attr") or {}
    for key in ("effect_id", "id", "resource_id"):
        val = ca.get(key)
        if val is not None and str(val).strip():
            return str(val).strip()
    # fallback scan
    for key in ("effect_id", "id", "resource_id"):
        val = item.get(key)
        if val is not None and str(val).strip():
            return str(val).strip()
    return None


def extract_display_name(item: dict, voice_type: str) -> str:
    ca = item.get("common_attr") or {}
    title = (ca.get("title") or "").strip()
    if title:
        return title

    dh = item.get("digital_human")
    if isinstance(dh, dict):
        for key in ("tone_type", "low_version_voice"):
            name = (dh.get(key) or "").strip()
            if name:
                return name

    for key in ("extra", "biz_extra"):
        parsed = parse_maybe_json(item.get(key))
        if isinstance(parsed, dict):
            alias = parsed.get("voice_alias_name") or parsed.get("name")
            if alias:
                return str(alias).strip()
            tonetype = parse_maybe_json(parsed.get("tonetype"))
            if isinstance(tonetype, dict) and tonetype.get("name"):
                name = str(tonetype["name"]).strip()
                if name:
                    return name
    return voice_type


def extract_lang(item: dict, voice_type: str) -> tuple[str, str]:
    for key in ("extra", "biz_extra", "common_attr"):
        blob = item.get(key)
        if key == "common_attr" and isinstance(blob, dict):
            # category / language fields if any
            for lk in ("language", "lang", "lan", "locale"):
                if blob.get(lk):
                    raw = str(blob[lk])
                    if "-" in raw:
                        return raw.split("-")[0].lower(), raw
                    return raw.lower(), LANG_MAP.get(raw.lower(), raw)
        parsed = parse_maybe_json(blob)
        if isinstance(parsed, dict):
            for lk in ("language", "lang", "lan", "locale"):
                if parsed.get(lk):
                    raw = str(parsed[lk])
                    if "-" in raw:
                        return raw.split("-")[0].lower(), raw
                    return raw.lower(), LANG_MAP.get(raw.lower(), raw)
    return guess_lang_from_voice_type(voice_type)


def iter_effect_items(payload: Any):
    if isinstance(payload, dict):
        data = payload.get("data") if isinstance(payload.get("data"), dict) else payload

        if isinstance(data, dict):
            for key in ("effect_item_list", "specific_item_list", "item_list", "list"):
                items = data.get(key)
                if isinstance(items, list):
                    for it in items:
                        if isinstance(it, dict):
                            yield it

            # Panel format: data.category_resources[category_id].effect_item_list
            cat_res = data.get("category_resources")
            if isinstance(cat_res, dict):
                for cat_payload in cat_res.values():
                    yield from iter_effect_items(cat_payload)
            elif isinstance(cat_res, list):
                for cat_payload in cat_res:
                    yield from iter_effect_items(cat_payload)

            for key in ("category_list", "categories", "panel_list"):
                cats = data.get(key)
                if isinstance(cats, list):
                    for cat in cats:
                        yield from iter_effect_items(cat)

        # Avoid infinite recursion on already-handled top-level by walking remaining dict values
        for k, v in payload.items():
            if k == "data":
                continue
            if isinstance(v, (dict, list)):
                yield from iter_effect_items(v)
    elif isinstance(payload, list):
        for it in payload:
            if isinstance(it, dict) and (
                "common_attr" in it or "timbre" in it or "digital_human" in it
            ):
                yield it
            else:
                yield from iter_effect_items(it)


def voices_from_payload(payload: Any, captured_at: str | None = None) -> list[dict]:
    captured_at = captured_at or now_iso()
    out: list[dict] = []
    seen_local: set[str] = set()
    for item in iter_effect_items(payload):
        voice_type = extract_voice_type(item)
        if not voice_type:
            continue
        resource_id = extract_resource_id(item, voice_type)
        if not resource_id:
            continue
        key = voice_type
        if key in seen_local:
            continue
        seen_local.add(key)
        lan, lang = extract_lang(item, voice_type)
        display_name = extract_display_name(item, voice_type)
        out.append(
            {
                "lan": lan,
                "lang": lang,
                "voice_type": voice_type,
                "display_name": display_name,
                "resource_id": str(resource_id),
                "captured_at": captured_at,
            }
        )
    return out


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as fp:
        return json.load(fp)


def merge_voices(existing: list[dict], incoming: list[dict]) -> tuple[list[dict], dict]:
    by_type: dict[str, dict] = {}
    for v in existing:
        vt = v.get("voice_type")
        if vt:
            by_type[vt] = dict(v)

    stats = {"added": 0, "updated": 0, "unchanged": 0, "skipped": 0}
    for v in incoming:
        vt = v.get("voice_type")
        rid = v.get("resource_id")
        if not vt or not rid:
            stats["skipped"] += 1
            continue
        if vt not in by_type:
            by_type[vt] = v
            stats["added"] += 1
            continue
        cur = by_type[vt]
        changed = False
        # resource_id: only fill if missing; never clobber a known good id with another panel's id
        if rid and not cur.get("resource_id"):
            cur["resource_id"] = rid
            changed = True
        # display_name: only fill if empty / still raw voice_type code
        cur_name = (cur.get("display_name") or "").strip()
        new_name = (v.get("display_name") or "").strip()
        if new_name and (not cur_name or cur_name == vt) and new_name != vt:
            cur["display_name"] = new_name
            changed = True
        # lang: fill unknown only
        if v.get("lang") and v["lang"] != "und" and (
            not cur.get("lang") or cur.get("lang") == "und"
        ):
            cur["lang"] = v["lang"]
            cur["lan"] = v.get("lan") or cur.get("lan")
            changed = True
        if changed:
            cur["captured_at"] = v.get("captured_at") or now_iso()
            stats["updated"] += 1
        else:
            stats["unchanged"] += 1

    merged = sorted(by_type.values(), key=lambda x: (x.get("lang") or "", x.get("display_name") or "", x.get("voice_type") or ""))
    return merged, stats


def collect_from_paths(paths: list[Path]) -> list[dict]:
    all_voices: list[dict] = []
    for path in paths:
        if not path.exists():
            print(f"[skip] missing: {path}")
            continue
        try:
            payload = load_json(path)
        except Exception as exc:
            print(f"[skip] bad json {path}: {exc}")
            continue
        voices = voices_from_payload(payload)
        print(f"[ok] {path.name}: {len(voices)} voices")
        all_voices.extend(voices)
    return all_voices


def main() -> None:
    ap = argparse.ArgumentParser(description="Merge captured CapCut voice lists into Voice.json")
    ap.add_argument(
        "--captures",
        nargs="*",
        help="Capture JSON files (default: captured_voices_*.json in project root)",
    )
    ap.add_argument("--voice-file", default=str(DEFAULT_VOICE_FILE))
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if args.captures:
        paths = [Path(p) for p in args.captures]
    else:
        paths = sorted(ROOT.glob("captured_voices_*.json"))

    existing_path = Path(args.voice_file)
    existing = load_json(existing_path) if existing_path.exists() else []
    if not isinstance(existing, list):
        raise SystemExit("Voice.json must be a JSON array")

    incoming = collect_from_paths(paths)
    merged, stats = merge_voices(existing, incoming)

    print("---")
    print(f"existing: {len(existing)}")
    print(f"incoming unique candidates: {len({v['voice_type'] for v in incoming})}")
    print(f"merged: {len(merged)}")
    print(f"stats: {stats}")

    if args.dry_run:
        print("dry-run: not writing")
        return

    with existing_path.open("w", encoding="utf-8") as fp:
        json.dump(merged, fp, ensure_ascii=False, indent=2)
        fp.write("\n")
    print(f"wrote {existing_path}")


if __name__ == "__main__":
    main()
