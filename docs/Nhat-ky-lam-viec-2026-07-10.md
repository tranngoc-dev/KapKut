# Nhật ký làm việc — CapCut TTS/STT Studio

**Ngày:** 2026-07-10  
**Dự án:** `capcut-tts-api-main`  
**Người yêu cầu:** Sếp (owner dự án)  
**Thực hiện:** Grok (assistant)

---

## 1. Mục tiêu tổng quát trong ngày

Làm việc theo chuỗi yêu cầu liên tiếp trên codebase CapCut TTS/STT:

1. Đánh giá hiện trạng dự án (audit).
2. Cập nhật / làm sạch danh sách giọng đọc từ CapCut PC.
3. Nâng UI lọc giọng, nhãn, nghe thử, chú thích engine.
4. Xây pipeline **kịch bản text → voice-over** (phục vụ tạo video).
5. Xây pipeline **audio → timestamp → TXT/SRT** (phục vụ phụ đề/kịch bản có mốc thời gian).
6. Ghi lại toàn bộ nội dung làm việc vào file `.md` (tài liệu này).

---

## 2. Các yêu cầu của Sếp (theo thứ tự hội thoại)

| # | Yêu cầu của Sếp | Ghi chú |
|---|-----------------|---------|
| 1 | **Audit dự án** | Đánh giá kiến trúc, bảo mật, chất lượng code, rủi ro, roadmap. |
| 2 | **Capture / cập nhật giọng đọc** khi CapCut PC đã mở | Bổ sung voice vào `Voice.json`. |
| 3 | **Làm lần lượt** các bước sau capture | Map lang → lọc sạch → health-check → export lại cache. |
| 4 | **Bộ lọc giọng đọc** theo ngôn ngữ, giới tính; **nhãn chi tiết**; **nghe thử** | + gợi ý chức năng phát triển thêm (workflow tạo video từ kịch bản text). |
| 5 | **Làm lần lượt P0** theo gợi ý | Multi-scene TTS, preset, smart split, batch ZIP. |
| 6 | **Giải thích model/loại giọng BV, ICL** | Kiến thức sản phẩm / catalog CapCut. |
| 7 | **Thêm chú thích** engine (BV/ICL/…) trên UI | Không chỉ giải thích chat. |
| 8 | **Upload audio (mp3, wav) → timestamp chính xác → xuất TXT** (timestamp đầu mỗi câu) | Dùng STT CapCut. |
| 9 | Phản hồi format SRT / cue thiếu chữ / ví dụ cue thật | Sửa format + gộp câu ngắn. |
| 10 | **Có** (đồng ý làm **gộp câu ngắn** liền kề) | Ví dụ: *em chỗ mua cái* + *váy này*. |
| 11 | **Ghi nhật ký làm việc ngày hôm nay ra file `.md`** | File này. |

---

## 3. Công việc đã làm (chi tiết)

### 3.1. Audit dự án

**Đã làm:**

- Rà soát cấu trúc repo, entry points (`main.py`, `server.py`, `capcut_common_task_client.py`, `app_gui.py`, `static/`, `Voice.json`).
- Báo cáo điểm mạnh / yếu: client reverse CapCut khá chắc; web API thiếu auth, race `DEFAULT_DEVICE`, thiếu tests, thiếu `requirements.txt` / `.gitignore`, artifact capture ~chục MB.
- Đề xuất roadmap P0–P3 (hygiene, concurrency, docs, product).

**Kết quả giao Sếp:** báo cáo audit trong chat (điểm ~5.5/10 cho readiness production).

**File liên quan (đã có sẵn, không refactor lớn sau audit):** toàn bộ source chính.

---

### 3.2. Cập nhật Voice.json từ CapCut PC

**Đã làm:**

- Xác nhận CapCut PC chạy (vd. bản **8.9.1**).
- Thử mitmproxy: CapCut **không** đi qua system proxy ổn định → chuyển sang đọc **cache local**  
  `%LOCALAPPDATA%\CapCut\User Data\Cache\ressdk_db\*\rp.db` bảng `http_cache`.
- Viết tool:
  - `tools/export_voices_from_capcut_http_cache.py`
  - `tools/merge_voices_from_captures.py`
  - `tools/mitm_capcut_voice_capture.py` (dự phòng)
  - `tools/cleanup_voice_registry.py`
  - `tools/healthcheck_voices.py`
- Merge + cleanup theo thứ tự:
  1. Map `lang` cho giọng `und`.
  2. Lọc junk / non-TTS shape.
  3. Health-check TTS sample.
  4. Loại **alnum 11labs** + **Azure Neural** (fail `TTSInvalidSpeaker`).
  5. Export lại cache (merge path Windows “filename too long” với 788 file — không ảnh hưởng registry đã sạch).

**Kết quả số liệu (tham chiếu cuối ngày):**

| Mốc | Số giọng |
|-----|----------|
| Trước | ~414 |
| Sau capture thô | ~1033 |
| Sau map/lọc/health | **~831** (BV/ICL/DiT/multi/SAMI usable) |

**Backup:** các file dạng `Voice.bak_*.json` (nếu còn trên máy).

---

### 3.3. UI lọc giọng + nhãn + nghe thử

**Đã làm:**

- API `/api/voices` trả metadata: `gender`, `engine`, `styles`, `tags`, `option_label`, `lang_labels`, `stats`.
- UI TTS:
  - Lọc ngôn ngữ (dynamic), giới tính, engine, ô tìm kiếm.
  - Thẻ chi tiết giọng + chip nhãn.
  - Nghe thử (nút cạnh select + trên thẻ chi tiết).
- Hàm gợi ý gender/engine/style: `guess_gender`, `detect_engine`, `detect_style_tags`, `enrich_voice_item` trong `server.py`.

**File:** `server.py`, `static/index.html`, `static/app.js`, `static/style.css`.

---

### 3.4. Pipeline kịch bản → Video VO (P0)

**Đã làm:**

- Module `script_tts.py`: parse scene (`---` / `# heading` / đoạn / single), smart split theo `max_chars`, SRT offset/merge, sanitize filename.
- Backend:
  - `POST /api/script/preview` — chỉ phân tích (không gọi CapCut).
  - `POST /api/script/render` — job nền TTS từng đoạn.
  - `GET /api/script/progress/{task_id}` — SSE.
  - `GET /api/script/download/{task_id}` — ZIP.
  - Refactor `run_tts_once()` dùng chung với `/api/tts`.
- ZIP output:
  ```text
  script.txt, meta.json, preset.json
  segments/NN_*.mp3 + .srt + .txt
  full/voiceover.mp3 + voiceover.srt
  ```
- UI tab **「Kịch bản → Video VO」**: textarea kịch bản, split mode, max chars, voice/rate/gap, preset localStorage, preview, render, progress, download.
- Smoke test thật: 1 đoạn ngắn BV074 → completed, có `full/voiceover.mp3`.

**File:** `script_tts.py`, `server.py`, `static/*`.

---

### 3.5. Giải thích + chú thích BV / ICL (và họ liên quan)

**Đã làm (chat):**

- **BV**: catalog classic `BV###_streaming` — ổn định, VO/tutorial.
- **ICL**: character/persona `ICL_en_male_…` — biểu cảm, shorts/story.
- Cùng pipeline SAMI / `sami_text_to_speech`; khác họ mã speaker.
- Nhắc thêm DiT / Multi / SAMI prefix.

**Đã làm (UI):**

- Ô **「📘 Chú thích loại model」** dưới filter engine.
- Legend click để lọc; highlight engine đang chọn.
- Chú thích engine trên thẻ chi tiết giọng.
- Gợi ý ngắn trên tab Kịch bản.

---

### 3.6. Audio → Timestamp TXT/SRT

**Đã làm:**

- Mở rộng `POST /api/stt`:
  - Input: file audio/video + `language` + `txt_style`.
  - Output: `timestamped_txt`, `lines`, `srt`, `line_count`, …
- Formatter `utterances_to_timestamped_txt()`:
  - `start` / `range` / `plain` / `srt_line` / `srt_block`.
- UI tab đổi tên **「Audio → Timestamp」**:
  - Upload MP3/WAV (ưu tiên), preview TXT, tải `.txt` + `.srt`.

**Sửa lỗi / tinh chỉnh theo phản hồi Sếp:**

1. **Cue SRT thiếu chữ** (chỉ có số + time):
   - Bỏ utterance `text` rỗng; đánh số lại.
2. **Ví dụ cue thật** (`em chỗ mua cái` / `váy này`):
   - Thêm **gộp câu ngắn liền kề** (mặc định bật).
   - Áp dụng cho cả TXT và SRT.
   - UI: checkbox gộp + slider khe hở max (ms).
   - Test unit:  
     `em chỗ mua cái` + `váy này` → một cue  
     `00:00:00,940 --> 00:00:03,100` + text gộp.

**File:** `script_tts.py` (`merge_utterances`, `utterances_to_srt_string`, …), `server.py`, `static/*`.

---

### 3.7. Cải tiến phụ trợ trong ngày

- `yt_dlp` import optional (TTS/script vẫn chạy khi chưa cài yt-dlp).
- Proxy mitm: bật thử rồi **tắt lại** (không để kẹt máy Sếp).
- Xóa dump `captured_voices_cache_*.json` tạm sau merge (tránh phình repo ~hàng trăm MB).

---

## 4. Việc chưa làm / còn trong kế hoạch đã thảo luận

Phân loại theo các roadmap đã nêu trong audit + gợi ý “tạo video từ kịch bản text”.

### 4.1. Từ audit (chưa implement trong ngày)

| Hạng mục | Mô tả | Ưu tiên đã gợi ý |
|----------|--------|------------------|
| `.gitignore` + dọn artifact hẳn | Không commit `__pycache__`, capture dump, screenshot debug | P0 |
| `requirements.txt` / pin deps | fastapi, uvicorn, requests, yt-dlp, playwright, pywebview… | P0 |
| Sửa race `DEFAULT_DEVICE` triệt để | Per-request device (đã có random id nhưng vẫn mutate global) | P0 |
| Auth / CORS chặt | Không public API mở `*` nếu deploy mạng | P1–P2 |
| Tests / CI | Smoke sign, SRT, merge cues, script parse | P1 |
| Gộp logic `main.py` ↔ `capcut_common_task_client.py` | Một module CapCut shared | P1 |
| Blocking I/O trên FastAPI async | `run_in_executor` / httpx async | P1 |
| Git history sạch | Repo lúc audit: chưa có commit / full untracked | Ops |

### 4.2. P1–P2 product (đã gợi ý, chưa code)

| Hạng mục | Mô tả |
|----------|--------|
| **Multi-speaker kịch bản** | Tag `[Nam]` / `[Nữ]` / `Speaker1:` map giọng khác nhau |
| **SSML nhẹ** | Pause, nhấn mạnh, rate từng đoạn |
| **So sánh 2–3 giọng** | Cùng 1 câu, preview song song (A/B) |
| **Voice health badge** | Cờ dead/OK trên UI từ health-check hàng loạt |
| **Queue job + lịch sử** | Hàng đợi TTS/STT, retry, log theo dự án |
| **Timeline / draft CapCut** | Xuất cấu trúc gắn timeline (ngoài MP3+SRT) |
| **Gợi ý B-roll** | Keyword scene → stock/local folder |
| **Export gói đăng** | title/desc/thumbnail prompt kèm VO |
| **Cache preview giọng** | Tránh gọi full `/api/tts` mỗi lần nghe thử |

### 4.3. Audio timestamp — mở rộng chưa làm

| Hạng mục | Mô tả |
|----------|--------|
| Health-check / merge config tinh hơn | Gộp theo dấu câu tiếng Việt nâng cao, speaker diarization |
| Batch nhiều file audio → nhiều TXT | Folder in / folder out |
| Chỉnh word-level timestamp | Hiện dùng utterance-level (sau gộp); word-level tốn STT chi tiết hơn |
| Preview audio + highlight dòng theo thời gian | Player đồng bộ click dòng transcript |

### 4.4. Voice registry — chưa làm hết

| Hạng mục | Mô tả |
|----------|--------|
| Health-check hàng loạt 50–100+ giọng | Ghi file dead list, ẩn trên UI |
| Map lang còn sót / multi gán đúng UI filter | Frontend filter “multi”, `ms-MY`, `zh-HK` đã có data nhưng UX có thể tinh thêm |
| Gender metadata chính thức | Hiện heuristic, chưa field chuẩn từ CapCut |

---

## 5. File / module chính phát sinh hoặc chỉnh trong ngày

```text
tools/
  export_voices_from_capcut_http_cache.py
  merge_voices_from_captures.py
  mitm_capcut_voice_capture.py
  cleanup_voice_registry.py
  healthcheck_voices.py
  healthcheck_result.json          # kết quả smoke TTS (nếu còn)
  scan_capcut_cache_for_voices.py  # phụ
  inspect_ressdk_db.py             # phụ

script_tts.py                      # parse script + timestamp/merge SRT/TXT
server.py                          # API voices / script / stt / tts refactor
static/index.html, app.js, style.css
Voice.json                         # registry sau capture + cleanup
docs/Nhat-ky-lam-viec-2026-07-10.md  # file này
```

---

## 6. Trạng thái tính năng (snapshot cuối ngày)

| Tính năng | Trạng thái |
|-----------|------------|
| CLI CapCut TTS/STT client | Có sẵn (trước ngày); vẫn dùng |
| Web TTS + filter/nhãn/preview + chú thích engine | **Đã có** |
| Tab Kịch bản → ZIP VO | **Đã có** (smoke OK) |
| Tab Audio → Timestamp TXT/SRT + gộp câu | **Đã có** |
| TikTok scraper | Có sẵn (phụ thuộc yt-dlp/playwright/ffmpeg) |
| Auth, tests, requirements, gitignore chuẩn | **Chưa** |
| Multi-speaker / SSML / health badge / queue | **Chưa** (đã lên kế hoạch) |

---

## 7. Cách Sếp kiểm tra nhanh các phần đã làm

```powershell
cd C:\Users\Trong\Desktop\capcut-tts-api-main
python server.py
# Mở http://127.0.0.1:8000 — Ctrl+F5
```

1. **TTS:** lọc lang/gender/engine, xem chú thích BV/ICL, nghe thử.  
2. **Kịch bản → Video VO:** dán script có `---` → Preview → Render → tải ZIP.  
3. **Audio → Timestamp:** upload MP3/WAV → bật “Gộp câu ngắn” → tải `.txt` / `.srt`.

---

## 8. Ghi chú vận hành / rủi ro (nhắc lại)

- CapCut API / sign / device: reverse-engineer; có thể gãy khi app đổi bản.
- Device ID random + mutate global: vẫn rủi ro concurrency.
- Timestamp phụ thuộc chất lượng ASR CapCut (ồn, nhạc, giọng nhỏ).
- Không deploy public khi CORS `*` và không auth.
- Tool capture voice dựa cache local CapCut PC đã login/dùng TTS panel.

---

## 9. Đề xuất thứ tự làm tiếp (nếu Sếp tiếp tục)

1. **P0 kỹ thuật:** `.gitignore` + `requirements.txt` + device per-request (hết race).  
2. **P1 product VO:** multi-speaker script + so sánh 2–3 giọng.  
3. **P1 timestamp:** batch folder audio → TXT/SRT.  
4. **P2:** health badge giọng + queue job/lịch sử dự án.

---

*Tài liệu được ghi theo đúng nội dung trao đổi và việc đã thực hiện trong phiên làm việc; các số liệu voice/health-check lấy từ kết quả chạy thực tế trong session.*
