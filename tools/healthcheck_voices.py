#!/usr/bin/env python3
"""Smoke-test CapCut TTS for a sample of Voice.json entries."""

from __future__ import annotations

import argparse
import json
import sys
import time
from copy import deepcopy
from pathlib import Path
from urllib.parse import urlencode

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from capcut_common_task_client import (  # noqa: E402
    DEFAULT_DEVICE,
    base_headers,
    checked_json_response,
    common_query,
    compact_json,
    load_json,
    make_sign_header,
    tts_new_body,
)

try:
    import requests
except ImportError:
    raise SystemExit("pip install requests")

BASE = "https://editor-api-sg.capcutapi.com"


def build_tts_request(text: str, voice: str, resource_id: str, rate: str, device: dict):
    babi, body = tts_new_body([text], voice, resource_id, rate, device)
    path = "/lv/v1/common_task/new"
    query = common_query(device, babi, include_region=True)
    body_text = compact_json(body)
    url = BASE + path + "?" + urlencode(query)
    headers = base_headers(device, body_text, appid=True)
    headers["sign"] = make_sign_header(url, device["appvr"], headers["device-time"], device["tdid"])
    return url, headers, body_text


def build_query_request(task_id: str, token: str, device: dict):
    body = {
        "tasks": [
            {
                "bind_id": "",
                "id": task_id,
                "req_key": "sami_text_to_speech",
                "task_version": "v3",
                "token": token,
            }
        ]
    }
    body_text = compact_json(body)
    path = "/lv/v1/common_task/query"
    query = common_query(device, None, include_region=False)
    url = BASE + path + "?" + urlencode(query)
    headers = base_headers(device, body_text, appid=True)
    headers["sign"] = make_sign_header(url, device["appvr"], headers["device-time"], device["tdid"])
    return url, headers, body_text


def test_voice(voice: dict, device: dict, text: str, polls: int = 15) -> dict:
    vt = voice["voice_type"]
    rid = str(voice["resource_id"])
    dev = deepcopy(device)
    try:
        url, headers, body_text = build_tts_request(text, vt, rid, "1.0", dev)
        resp = requests.post(url, headers=headers, data=body_text.encode("utf-8"), timeout=60)
        data = checked_json_response(resp, "tts-new")
        # CapCut ret codes
        if str(data.get("ret")) not in ("0", "0.0", "") and data.get("ret") not in (0, None):
            return {
                "voice_type": vt,
                "ok": False,
                "stage": "new",
                "detail": f"ret={data.get('ret')} errmsg={data.get('errmsg')} {str(data)[:240]}",
            }
        tasks = (data.get("data") or {}).get("tasks") or []
        if not tasks:
            return {"voice_type": vt, "ok": False, "stage": "new", "detail": str(data)[:300]}
        task_id = tasks[0].get("id")
        token = tasks[0].get("token")
        if not task_id or not token:
            return {"voice_type": vt, "ok": False, "stage": "new", "detail": str(tasks[0])[:300]}

        for i in range(polls):
            time.sleep(1)
            q_url, q_headers, q_body = build_query_request(task_id, token, dev)
            q_resp = requests.post(q_url, headers=q_headers, data=q_body.encode("utf-8"), timeout=60)
            q_data = checked_json_response(q_resp, "tts-query")
            task = ((q_data.get("data") or {}).get("tasks") or [{}])[0]
            status = task.get("status")
            if status in ("succeed", 2, "succeeded", "success"):
                payload_raw = task.get("payload") or "{}"
                try:
                    payload = json.loads(payload_raw) if isinstance(payload_raw, str) else payload_raw
                except Exception:
                    payload = {}
                subs = payload.get("audio_subtitles") or []
                speech = (subs[0] or {}).get("speech_url") if subs else None
                return {
                    "voice_type": vt,
                    "display_name": voice.get("display_name"),
                    "lang": voice.get("lang"),
                    "ok": bool(speech),
                    "stage": "query",
                    "polls": i + 1,
                    "speech_url": (speech or "")[:80],
                    "detail": None if speech else "no speech_url",
                }
            if status in ("failed", "fail", 3):
                return {
                    "voice_type": vt,
                    "ok": False,
                    "stage": "query",
                    "detail": str(task.get("detail_info") or task)[:300],
                }
        return {"voice_type": vt, "ok": False, "stage": "timeout", "detail": f"last_status={status}"}
    except Exception as exc:
        return {"voice_type": vt, "ok": False, "stage": "exception", "detail": str(exc)[:300]}


def pick_sample(voices: list[dict], n: int) -> list[dict]:
    """Prefer diversity: baseline BV074 + one per lang family + some new."""
    by_type = {v["voice_type"]: v for v in voices}
    picked: list[dict] = []
    seen = set()

    def add(vt: str | None = None, pred=None):
        if vt and vt in by_type and vt not in seen:
            picked.append(by_type[vt])
            seen.add(vt)
            return
        if pred:
            for v in voices:
                if v["voice_type"] in seen:
                    continue
                if pred(v):
                    picked.append(v)
                    seen.add(v["voice_type"])
                    return

    add("BV074_streaming")
    add(pred=lambda v: v.get("lang") == "vi-VN" and v["voice_type"].startswith("BV") and "BV074" not in v["voice_type"])
    add(pred=lambda v: v.get("lang") == "en-US" and v["voice_type"].startswith("en_"))
    add(pred=lambda v: v.get("lang") == "en-US" and v["voice_type"].startswith("ICL_"))
    add(pred=lambda v: v.get("lang") == "zh-CN" and v["voice_type"].startswith(("zh_", "ICL_", "BV")))
    add(pred=lambda v: v.get("lang") == "ja-JP")
    add(pred=lambda v: v.get("lang") == "id-ID")
    add(pred=lambda v: v.get("lang") == "es-ES")
    add(pred=lambda v: str(v.get("voice_type", "")).startswith("DiT_"))
    add(pred=lambda v: str(v.get("voice_type", "")).startswith("multi_"))
    add(pred=lambda v: len(v.get("voice_type") or "") == 20 and (v.get("voice_type") or "").isalnum())
    add(pred=lambda v: "Neural" in (v.get("voice_type") or ""))
    # fill with newest captures
    for v in sorted(voices, key=lambda x: x.get("captured_at") or "", reverse=True):
        if len(picked) >= n:
            break
        if v["voice_type"] not in seen:
            picked.append(v)
            seen.add(v["voice_type"])
    return picked[:n]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--voice-file", default=str(ROOT / "Voice.json"))
    ap.add_argument("--device-json", default=str(ROOT / "device.json"))
    ap.add_argument("--n", type=int, default=12)
    ap.add_argument("--text", default="Hello, this is a CapCut TTS health check.")
    ap.add_argument("--out", default=str(ROOT / "tools" / "healthcheck_result.json"))
    args = ap.parse_args()

    voices = json.loads(Path(args.voice_file).read_text(encoding="utf-8"))
    device = deepcopy(DEFAULT_DEVICE)
    if Path(args.device_json).exists():
        device.update(load_json(args.device_json, {}))

    sample = pick_sample(voices, args.n)
    print(f"Testing {len(sample)} voices with device_id={device.get('device_id')}")
    results = []
    for i, v in enumerate(sample, 1):
        print(f"[{i}/{len(sample)}] {v.get('lang')} | {v['voice_type']} | {v.get('display_name')}")
        r = test_voice(v, device, args.text)
        results.append(r)
        flag = "OK" if r.get("ok") else "FAIL"
        print(f"   -> {flag} stage={r.get('stage')} {r.get('detail') or r.get('speech_url') or ''}")

    ok = sum(1 for r in results if r.get("ok"))
    summary = {"ok": ok, "total": len(results), "results": results}
    Path(args.out).write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"\nSummary: {ok}/{len(results)} OK")
    print(f"wrote {args.out}")
    # exit non-zero if baseline BV074 fails hard
    base = next((r for r in results if r["voice_type"] == "BV074_streaming"), None)
    if base and not base.get("ok"):
        raise SystemExit(2)


if __name__ == "__main__":
    main()
