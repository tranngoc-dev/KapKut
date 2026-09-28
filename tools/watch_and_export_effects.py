#!/usr/bin/env python3
"""
Tự động theo dõi (Live Watcher) SQLite cache của CapCut PC.
Khi người dùng bấm vào các tab (Chuyển cảnh, Hiệu ứng, Động) trong CapCut PC,
tool sẽ lập tức bắt lấy dữ liệu mới và cập nhật vào Transitions.json, Animations.json, Video_Effects.json.
"""

import time
import sys
from pathlib import Path
from export_all_effects_from_cache import extract_effects

def watch():
    print("👀 Bắt đầu theo dõi cache CapCut PC theo thời gian thực...")
    print("👉 HƯỚNG DẪN DÀNH CHO SẾP TRÊN CAPCUT PC:")
    print("   1. Mở bất kỳ project nào trong CapCut PC.")
    print("   2. Bấm vào tab 'Chuyển cảnh' (Transitions) ở thanh menu phía trên/trái.")
    print("   3. Cuộn xem qua các danh mục (Trending, Basic, v.v.).")
    print("   4. Bấm vào 1 ảnh/video trên timeline -> Bấm tab 'Hiệu ứng động' (Animation).")
    print("-------------------------------------------------------------------------")
    
    last_counts = {}
    try:
        while True:
            counts = extract_effects()
            if counts != last_counts:
                print(f"✨ [CẬP NHẬT MỚI lúc {time.strftime('%H:%M:%S')}]: {counts}")
                last_counts = counts
            time.sleep(3)
    except KeyboardInterrupt:
        print("\nĐã dừng theo dõi.")

if __name__ == "__main__":
    watch()
