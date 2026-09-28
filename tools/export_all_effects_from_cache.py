#!/usr/bin/env python3
"""
Trích xuất tất cả hiệu ứng (Video Effects, Photo Effects, Transitions, Animations)
từ SQLite cache của CapCut PC (%LOCALAPPDATA%\\CapCut\\User Data\\Cache\\ressdk_db)
"""

import glob
import os
import sqlite3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = Path(os.environ["LOCALAPPDATA"]) / "CapCut" / "User Data" / "Cache" / "ressdk_db"

def extract_effects():
    video_effects = {}
    photo_effects = {}
    transitions = {}
    animations = {}
    other_effects = {}

    db_paths = list(BASE.rglob("rp*.db"))
    print(f"🔍 Tìm thấy {len(db_paths)} database rp*.db trong cache CapCut")

    for db in db_paths:
        try:
            con = sqlite3.connect(f"file:{db.as_posix()}?mode=ro", uri=True)
            rows = con.execute("SELECT id, url, response_body FROM http_cache").fetchall()
            for _id, url, body in rows:
                if not body:
                    continue
                try:
                    decoded = body.decode("utf-8", errors="ignore") if isinstance(body, bytes) else str(body)
                    if "effect_item_list" not in decoded and "category_resources" not in decoded:
                        continue
                    data = json.loads(decoded)
                    d = data.get("data", {})
                    if not isinstance(d, dict):
                        continue

                    items = d.get("effect_item_list") or []
                    # Also check category_resources
                    cat_res = d.get("category_resources", {})
                    if isinstance(cat_res, dict):
                        for c_data in cat_res.values():
                            if isinstance(c_data, dict):
                                items.extend(c_data.get("effect_item_list") or [])

                    url_lower = (url or "").lower()

                    for it in items:
                        if not isinstance(it, dict):
                            continue
                        ca = it.get("common_attr") or {}
                        eid = ca.get("effect_id") or ca.get("id") or it.get("id") or it.get("effect_id")
                        title = ca.get("title") or it.get("name") or it.get("title")
                        if not eid or not title:
                            continue

                        eid = str(eid)
                        title = str(title).strip()

                        cover = (
                            ca.get("cover_url", {}).get("small")
                            or ca.get("cover_url", {}).get("static_img")
                            or ca.get("cover_url", {}).get("uri")
                            or ""
                        )
                        item_urls = ca.get("item_urls") or []
                        md5 = ca.get("md5") or ""
                        source = ca.get("source")
                        effect_type = ca.get("effect_type")
                        tags = ca.get("tags") or []
                        extra = it.get("extra") or ca.get("extra") or ""

                        # Detect category / panel from URL
                        panel = "unknown"
                        if "transition" in url_lower:
                            panel = "transition"
                        elif "animation" in url_lower or "animate" in url_lower:
                            panel = "animation"
                        elif "video_capcutpc" in url_lower or "video" in url_lower:
                            panel = "video_effect"
                        elif "ai_painting" in url_lower or "photo" in url_lower:
                            panel = "photo_effect"

                        record = {
                            "id": eid,
                            "title": title,
                            "panel": panel,
                            "effect_type": effect_type,
                            "cover_url": cover,
                            "item_urls": item_urls,
                            "md5": md5,
                            "tags": tags,
                        }

                        blob = (url_lower + " " + title.lower() + " " + str(extra).lower())

                        if "transition" in blob:
                            transitions[eid] = record
                        elif "animation" in blob or panel == "animation":
                            animations[eid] = record
                        elif panel == "photo_effect" or "photo" in blob or "ai_painting" in blob:
                            photo_effects[eid] = record
                        elif panel == "video_effect" or "video" in blob:
                            video_effects[eid] = record
                        else:
                            other_effects[eid] = record

                except Exception:
                    pass
            con.close()
        except Exception as e:
            print(f"Lỗi đọc DB {db}: {e}")

    print(f"📊 Kết quả trích xuất hiện tại:")
    print(f"  - Hiệu ứng Video (Video Effects): {len(video_effects)}")
    print(f"  - Hiệu ứng Ảnh (Photo / AI Painting): {len(photo_effects)}")
    print(f"  - Chuyển cảnh (Transitions): {len(transitions)}")
    print(f"  - Hiệu ứng động cho ảnh/clip (Animations): {len(animations)}")
    print(f"  - Hiệu ứng khác: {len(other_effects)}")

    # Ghi ra file JSON
    if video_effects:
        out_v = ROOT / "Video_Effects.json"
        with open(out_v, "w", encoding="utf-8") as f:
            json.dump(list(video_effects.values()), f, ensure_ascii=False, indent=2)
        print(f"💾 Đã lưu {len(video_effects)} video effects vào: {out_v.name}")

    if photo_effects:
        out_p = ROOT / "Photo_Effects.json"
        with open(out_p, "w", encoding="utf-8") as f:
            json.dump(list(photo_effects.values()), f, ensure_ascii=False, indent=2)
        print(f"💾 Đã lưu {len(photo_effects)} photo effects vào: {out_p.name}")

    if transitions:
        out_t = ROOT / "Transitions.json"
        with open(out_t, "w", encoding="utf-8") as f:
            json.dump(list(transitions.values()), f, ensure_ascii=False, indent=2)
        print(f"💾 Đã lưu {len(transitions)} transitions vào: {out_t.name}")

    if animations:
        out_a = ROOT / "Animations.json"
        with open(out_a, "w", encoding="utf-8") as f:
            json.dump(list(animations.values()), f, ensure_ascii=False, indent=2)
        print(f"💾 Đã lưu {len(animations)} animations vào: {out_a.name}")

    return {
        "video_effects": len(video_effects),
        "photo_effects": len(photo_effects),
        "transitions": len(transitions),
        "animations": len(animations),
    }

if __name__ == "__main__":
    extract_effects()
