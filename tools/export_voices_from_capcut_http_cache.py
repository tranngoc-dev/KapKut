#!/usr/bin/env python3
"""Export CapCut voice/effect list payloads from local ressdk http_cache SQLite."""

from __future__ import annotations

import json
import os
import sqlite3
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = Path(os.environ["LOCALAPPDATA"]) / "CapCut" / "User Data" / "Cache" / "ressdk_db"


def is_voice_payload(body: str, url: str = "") -> bool:
    u = (url or "").lower()
    b = body or ""
    if "effect_item_list" in b:
        return True
    if "category_resources" in b and "voice" in b.lower():
        return True
    if "tonetype" in b and "voice_type" in b:
        return True
    if "digital_human" in b and "voice_type" in b:
        return True
    if any(k in u for k in ("tone", "voice", "tts", "timbre", "text_to_speech", "artist")):
        if "voice_type" in b or "effect_item_list" in b:
            return True
    return False


def main() -> None:
    ts = int(time.time())
    saved = 0
    seen_hash: set[int] = set()

    for db in BASE.rglob("rp.db"):
        print(f"DB {db}")
        try:
            con = sqlite3.connect(f"file:{db.as_posix()}?mode=ro", uri=True)
        except Exception as exc:
            print(f"  open err: {exc}")
            continue

        try:
            rows = con.execute(
                "SELECT id, url, response_body, timestamp FROM http_cache"
            ).fetchall()
        except Exception as exc:
            print(f"  query err: {exc}")
            con.close()
            continue

        print(f"  http_cache rows={len(rows)}")
        for _id, url, body, timestamp in rows:
            if body is None:
                continue
            if isinstance(body, bytes):
                try:
                    body = body.decode("utf-8")
                except Exception:
                    body = body.decode("utf-8", errors="ignore")
            if not isinstance(body, str) or len(body) < 100:
                continue
            if not is_voice_payload(body, url or ""):
                continue

            h = hash(body)
            if h in seen_hash:
                continue
            seen_hash.add(h)

            # parse to pretty JSON when possible
            try:
                obj = json.loads(body)
                text = json.dumps(obj, ensure_ascii=False, indent=2) + "\n"
            except Exception:
                obj = None
                text = body

            out = ROOT / f"captured_voices_cache_{ts}_{saved}.json"
            out.write_text(text, encoding="utf-8")
            saved += 1
            n_items = 0
            if isinstance(obj, dict):
                data = obj.get("data") or {}
                if isinstance(data, dict):
                    items = data.get("effect_item_list") or []
                    if isinstance(items, list):
                        n_items = len(items)
                    cat = data.get("category_resources")
                    if isinstance(cat, dict):
                        for v in cat.values():
                            if isinstance(v, dict) and isinstance(v.get("effect_item_list"), list):
                                n_items += len(v["effect_item_list"])
            print(f"  [saved] {out.name} url={(url or '')[:100]} items~{n_items} bytes={len(body)}")

        # also dump effect table rows if present
        try:
            effects = con.execute(
                "SELECT effect_id, title, extra, biz_extra, third_resource_id FROM effect WHERE extra IS NOT NULL OR biz_extra IS NOT NULL LIMIT 5000"
            ).fetchall()
        except Exception:
            effects = []
        if effects:
            print(f"  effect table rows with extra: {len(effects)}")
            payload = {
                "ret": "0",
                "errmsg": "from_effect_table",
                "data": {
                    "effect_item_list": [
                        {
                            "common_attr": {
                                "effect_id": eid,
                                "id": eid,
                                "title": title or "",
                                "extra": extra or "",
                            },
                            "extra": extra or "",
                            "biz_extra": biz or "",
                            "resource_id_hint": rid,
                        }
                        for eid, title, extra, biz, rid in effects
                    ]
                },
            }
            out = ROOT / f"captured_voices_cache_{ts}_effects_{saved}.json"
            out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            print(f"  [saved] {out.name}")
            saved += 1

        con.close()

    print(f"DONE saved={saved}")


if __name__ == "__main__":
    main()
