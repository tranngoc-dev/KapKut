import os
import sys
import json
import uuid
import time
import shutil
import tempfile
import zipfile
import re
import random
import threading
import subprocess
from copy import deepcopy
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse, PlainTextResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import requests

try:
    import yt_dlp
except ImportError:  # optional for script/TTS-only usage
    yt_dlp = None

# Add current dir to path to make imports easy
BASE_DIR = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

import main
from capcut_common_task_client import (
    build_request,
    checked_json_response,
    DEFAULT_DEVICE,
    load_json,
    tts_new_body,
    common_query,
    base_headers,
    make_sign_header,
    compact_json
)
from script_tts import (
    parse_script_scenes,
    expand_scenes_with_splits,
    simple_srt_for_segment,
    merge_srt_files,
    sanitize_filename,
    utterances_to_timestamped_txt,
    utterances_to_srt_string,
)

app = FastAPI(title="CapCut TTS & STT Web API")

def sanitize_tiktok_url(url: str) -> str:
    url = url.strip()
    if "/playlist/" in url:
        url = url.replace("/playlist/", "/collection/")
    return url


# Enable CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load Voice.json
VOICES_FILE = os.path.join(BASE_DIR, "Voice.json")
voices_data = []
if os.path.exists(VOICES_FILE):
    try:
        with open(VOICES_FILE, "r", encoding="utf-8") as f:
            voices_data = json.load(f)
    except Exception as e:
        print(f"Error loading Voice.json: {e}")

# Helper: Map voice_type to resource_id
voice_resource_map = {}
for voice in voices_data:
    voice_resource_map[voice["voice_type"]] = voice["resource_id"]

def capcut_to_srt_string(capcut_json, merge: bool = True, max_gap_ms: int = 450, max_chars: int = 100):
    """Build SRT from CapCut utterances; skip empty text; optional short-cue merge."""
    try:
        return utterances_to_srt_string(
            capcut_json,
            merge=merge,
            max_gap_ms=max_gap_ms,
            max_chars=max_chars,
        )
    except Exception as e:
        print(f"Error formatting SRT: {e}")
        return ""

class TTSArgs:
    def __init__(self, text, voice, resource_id, rate, pitch=0):
        self.mode = "tts-new"
        self.device_json = None
        self.dry_run = False
        self.text = [text]
        self.text_file = None
        self.voice = voice
        self.resource_id = resource_id
        self.rate = str(rate)
        self.pitch = int(pitch)

class TTSQueryArgs:
    def __init__(self, task_id, token):
        self.mode = "tts-query"
        self.device_json = None
        self.dry_run = False
        self.task_id = task_id
        self.token = token
        self.bind_id = ""


def apply_ephemeral_device_ids():
    """Assign random device ids for CapCut anti-bot (process-local)."""
    did = str(random.randint(1000000000000000000, 9999999999999999999))
    iid = str(random.randint(1000000000000000000, 9999999999999999999))
    tdid = str(random.randint(1000000000000000000, 9999999999999999999))
    for store in (DEFAULT_DEVICE, main.DEFAULT_DEVICE):
        store["device_id"] = did
        store["iid"] = iid
        store["tdid"] = tdid
    return did


def resolve_resource_id(voice: str, payload_resource_id=None) -> str:
    rid = voice_resource_map.get(voice)
    if rid:
        return str(rid)
    if payload_resource_id:
        return str(payload_resource_id)
    return "7102355709945188865"


def guess_stt_lang_from_voice(voice: str) -> str:
    vt = (voice or "").lower()
    mapping = [
        (("vi_", "vi-", "vietnamese"), "vi-VN"),
        (("en_", "en-", "english"), "en-US"),
        (("zh_", "zh-", "chinese"), "zh-CN"),
        (("ja_", "ja-", "japanese"), "ja-JP"),
        (("ko_", "ko-", "korean"), "ko-KR"),
        (("es_", "es-"), "es-ES"),
        (("fr_", "fr-"), "fr-FR"),
        (("de_", "de-"), "de-DE"),
    ]
    for keys, lang in mapping:
        if any(k in vt for k in keys):
            return lang
    # BV Vietnamese classics default
    if vt.startswith("bv") and any(x in vt for x in ("074", "075", "560", "562", "421")):
        return "vi-VN"
    return "vi-VN"


def run_tts_once(text: str, voice: str, rate=1.0, resource_id=None, pitch=0) -> dict:
    """
    Create one CapCut TTS task and poll until speech_url is ready.
    Returns {speech_url, duration_ms, text, voice}.
    """
    text = (text or "").strip()
    if not text:
        raise ValueError("Text cannot be empty")
    rid = resolve_resource_id(voice, resource_id)
    apply_ephemeral_device_ids()
    args = TTSArgs(text, voice, rid, rate, pitch=pitch)
    url, headers, body_text = build_request(args)
    resp = requests.post(url, headers=headers, data=body_text.encode("utf-8"), timeout=60)
    res_json = checked_json_response(resp, "tts-new")

    if str(res_json.get("ret")) not in ("0", "0.0", "") and res_json.get("ret") not in (0, None):
        raise RuntimeError(f"TTS new failed: ret={res_json.get('ret')} errmsg={res_json.get('errmsg')}")

    task = (res_json.get("data") or {}).get("tasks") or []
    if not task:
        raise RuntimeError(f"TTS new missing tasks: {res_json}")
    task_id = task[0].get("id")
    token = task[0].get("token")
    if not task_id or not token:
        raise RuntimeError(f"TTS new missing id/token: {task[0]}")

    speech_url = None
    duration_ms = 0
    last_status = None
    for _ in range(25):
        time.sleep(1)
        q_args = TTSQueryArgs(task_id, token)
        q_url, q_headers, q_body_text = build_request(q_args)
        q_resp = requests.post(q_url, headers=q_headers, data=q_body_text.encode("utf-8"), timeout=60)
        q_json = checked_json_response(q_resp, "tts-query")
        task_info = ((q_json.get("data") or {}).get("tasks") or [{}])[0]
        last_status = task_info.get("status")
        if last_status in ("succeed", 2, "succeeded", "success"):
            payload_str = task_info.get("payload", "{}")
            payload_json = json.loads(payload_str) if isinstance(payload_str, str) else (payload_str or {})
            subtitles = payload_json.get("audio_subtitles") or []
            if subtitles:
                speech_url = subtitles[0].get("speech_url")
                duration_ms = int(subtitles[0].get("duration") or 0)
            break
        if last_status in ("failed", "fail", 3):
            raise RuntimeError(f"TTS task failed: {task_info.get('detail_info') or task_info}")

    if not speech_url:
        raise TimeoutError(f"TTS polling timed out (last_status={last_status})")
    return {
        "speech_url": speech_url,
        "duration_ms": duration_ms,
        "text": text,
        "voice": voice,
        "resource_id": rid,
    }


def download_url_to_file(url: str, path: str, timeout: int = 60) -> int:
    resp = requests.get(url, timeout=timeout)
    resp.raise_for_status()
    with open(path, "wb") as fp:
        fp.write(resp.content)
    return len(resp.content)


def ffmpeg_concat_mp3(paths: list[str], out_path: str, gap_ms: int = 300) -> None:
    """Concatenate mp3 files with optional silence gap using ffmpeg."""
    if not paths:
        raise ValueError("No audio paths to concat")
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        # fallback: binary concat only works for same-codec mp3 sometimes — still try copy via filter
        raise RuntimeError("ffmpeg not found in PATH")

    work = tempfile.mkdtemp(prefix="tts_concat_")
    try:
        list_file = os.path.join(work, "list.txt")
        silence = os.path.join(work, "silence.mp3")
        gap_sec = max(0, int(gap_ms)) / 1000.0
        entries = []
        if gap_sec > 0 and len(paths) > 1:
            # gen short silence
            subprocess.run(
                [ffmpeg, "-y", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono", "-t", str(gap_sec), "-q:a", "9", silence],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
        with open(list_file, "w", encoding="utf-8") as fp:
            for i, p in enumerate(paths):
                # ffmpeg concat demuxer requires escaped quotes
                safe = p.replace("\\", "/").replace("'", "'\\''")
                fp.write(f"file '{safe}'\n")
                if gap_sec > 0 and i < len(paths) - 1:
                    ssafe = silence.replace("\\", "/").replace("'", "'\\''")
                    fp.write(f"file '{ssafe}'\n")
        # re-encode to normalize
        subprocess.run(
            [ffmpeg, "-y", "-f", "concat", "-safe", "0", "-i", list_file, "-c:a", "libmp3lame", "-q:a", "4", out_path],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    finally:
        shutil.rmtree(work, ignore_errors=True)


# In-memory script render jobs (local tool)
script_jobs: dict = {}


@app.get("/")
async def get_index():
    index_path = os.path.join(BASE_DIR, "static", "index.html")
    if os.path.exists(index_path):
        return FileResponse(
            index_path,
            headers={
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
                "Expires": "0",
            },
        )
    return PlainTextResponse("Static index.html not found. Please build frontend files.")

LANG_LABELS = {
    "vi-VN": "Tiếng Việt",
    "en-US": "Tiếng Anh (US)",
    "zh-CN": "Tiếng Trung",
    "zh-HK": "Tiếng Quảng Đông",
    "ja-JP": "Tiếng Nhật",
    "ko-KR": "Tiếng Hàn",
    "id-ID": "Tiếng Indonesia",
    "th-TH": "Tiếng Thái",
    "es-ES": "Tiếng Tây Ban Nha",
    "es-MX": "Tiếng Tây Ban Nha (MX)",
    "pt-BR": "Tiếng Bồ Đào Nha (BR)",
    "fr-FR": "Tiếng Pháp",
    "de-DE": "Tiếng Đức",
    "it-IT": "Tiếng Ý",
    "ms-MY": "Tiếng Malay",
    "ru-RU": "Tiếng Nga",
    "multi": "Đa ngôn ngữ",
    "und": "Chưa xác định",
}


def guess_gender(voice_type: str, display_name: str) -> str:
    vt = (voice_type or "").lower()
    dn = (display_name or "").lower()
    blob = f"{vt} {dn}"

    # Children / kid first
    if any(k in blob for k in ("child", "kid", "loli", "giọng bé", "trẻ con", "baby", "teen_girl", "teen_boy")):
        return "Trẻ em"

    # Explicit gender tokens in voice_type (highest signal)
    if re.search(r"(^|_)female(_|$)|girl|woman|lady|nữ", vt):
        return "Nữ"
    if re.search(r"(^|_)male(_|$)|boy|man(?!y)|nam", vt) and "female" not in vt:
        return "Nam"

    female_keywords = [
        "nữ", "cô gái", "cô ", "chị ", "bà ", "mẹ", "tiểu thư", "girl", "woman",
        "female", "lady", "fangirl", "idol", "aunt", "queen", "witch",
    ]
    male_keywords = [
        "nam", "chú ", "anh ", "ông ", "bố", "đại đế", "thầy", "tổng tài", "cậu",
        "boy", "man", "male", "uncle", "captain", "santa", "king", "hero",
    ]

    if any(k in dn for k in female_keywords):
        return "Nữ"
    if any(k in dn for k in male_keywords):
        return "Nam"
    return "Khác"


def detect_engine(voice_type: str) -> str:
    vt = voice_type or ""
    if vt.startswith("BV"):
        return "BV"
    if vt.startswith("ICL_"):
        return "ICL"
    if vt.startswith("DiT_"):
        return "DiT"
    if vt.startswith("multi_"):
        return "Multi"
    if re.match(r"^(en|zh|vi|ja|ko|id|th|es|pt|fr|de|it|ms|ru)_", vt, re.I):
        return "SAMI"
    return "Other"


def detect_style_tags(voice_type: str, display_name: str) -> list:
    blob = f"{voice_type or ''} {display_name or ''}".lower()
    rules = [
        ("ASMR", ("asmr", "whisper")),
        ("Narration", ("narrat", "story", "storytell", "kể chuyện")),
        ("News", ("news", "anchor", "broadcast", "tin tức", "jieshuo", "xinwen")),
        ("Cute", ("cute", "idol", "dễ thương", "kawaii", "cheery")),
        ("Serious", ("serious", "nghiêm", "formal", "serio")),
        ("Energetic", ("energetic", "excited", "lively", "sôi nổi", "cheer")),
        ("Robot", ("robot", "droid", "synth")),
        ("Demon", ("demon", "devil", "grim")),
        ("DSP", ("_dsp", "echo", "vibrato", "autotune")),
        ("Character", ("santa", "grinch", "deadpool", "anime", "witch", "captain")),
        ("Commercial", ("ad ", "ads", "commercial", "product", "guanggao", "promo")),
        ("Gentle", ("gentle", "soft", "calm", "cozy", "warm", "êm")),
    ]
    tags = []
    for label, keys in rules:
        if any(k in blob for k in keys):
            tags.append(label)
    return tags[:4]


def enrich_voice_item(voice: dict) -> dict:
    voice_type = voice.get("voice_type") or ""
    display_name = voice.get("display_name") or voice_type
    lang = voice.get("lang") or "und"
    gender = guess_gender(voice_type, display_name)
    engine = detect_engine(voice_type)
    styles = detect_style_tags(voice_type, display_name)
    lang_label = LANG_LABELS.get(lang, lang)

    tags = [lang_label, gender, engine] + styles
    # compact label for <option>
    option_label = f"{display_name} - {voice_type} | {lang}"

    return {
        "voice_type": voice_type,
        "display_name": display_name,
        "option_label": option_label,
        "resource_id": voice.get("resource_id"),
        "lang": lang,
        "lan": voice.get("lan") or (lang.split("-")[0] if lang else "und"),
        "lang_label": lang_label,
        "gender": gender,
        "engine": engine,
        "styles": styles,
        "tags": tags,
        "captured_at": voice.get("captured_at"),
    }


@app.get("/api/voices")
async def get_voices():
    """Return voices grouped by lang + filter metadata for UI."""
    languages = {}
    stats = {"total": 0, "by_lang": {}, "by_gender": {}, "by_engine": {}}

    for voice in voices_data:
        item = enrich_voice_item(voice)
        lang = item["lang"]
        languages.setdefault(lang, []).append(item)
        stats["total"] += 1
        stats["by_lang"][lang] = stats["by_lang"].get(lang, 0) + 1
        stats["by_gender"][item["gender"]] = stats["by_gender"].get(item["gender"], 0) + 1
        stats["by_engine"][item["engine"]] = stats["by_engine"].get(item["engine"], 0) + 1

    # Stable sort inside each language
    for lang, items in languages.items():
        items.sort(key=lambda x: ((x.get("display_name") or "").lower(), x.get("voice_type") or ""))

    return JSONResponse(
        content={
            "languages": languages,
            "lang_labels": LANG_LABELS,
            "stats": stats,
            "filters": {
                "genders": ["Nam", "Nữ", "Trẻ em", "Khác"],
                "engines": ["BV", "ICL", "DiT", "Multi", "SAMI", "Other"],
            },
        }
    )

def split_text_into_chunks(text: str, max_chars: int = 4000) -> list[str]:
    """
    Split text into chunks of maximum max_chars without cutting sentences abruptly.
    Splits by paragraphs first, then by punctuation (. ! ? \n), then by spaces if necessary.
    """
    text = (text or "").strip()
    if not text:
        return []
    if len(text) <= max_chars:
        return [text]

    chunks = []
    paragraphs = text.split("\n")
    current_chunk = ""

    for para in paragraphs:
        para_str = para.strip()
        if not para_str:
            continue

        if len(para_str) > max_chars:
            # Paragraph itself is too large, split by sentence endings
            sentences = re.split(r'(?<=[.!?])\s+', para_str)
            for sent in sentences:
                sent_str = sent.strip()
                if not sent_str:
                    continue
                if len(sent_str) > max_chars:
                    # Fallback to word splitting if sentence exceeds limit
                    words = sent_str.split(" ")
                    for word in words:
                        if len(current_chunk) + len(word) + 1 > max_chars:
                            if current_chunk:
                                chunks.append(current_chunk.strip())
                                current_chunk = ""
                        current_chunk += (" " if current_chunk else "") + word
                else:
                    if len(current_chunk) + len(sent_str) + 1 > max_chars:
                        if current_chunk:
                            chunks.append(current_chunk.strip())
                            current_chunk = ""
                    current_chunk += ("\n" if current_chunk else "") + sent_str
        else:
            if len(current_chunk) + len(para_str) + 1 > max_chars:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                    current_chunk = ""
            current_chunk += ("\n" if current_chunk else "") + para_str

    if current_chunk.strip():
        chunks.append(current_chunk.strip())

    return chunks


@app.post("/api/tts")
async def text_to_speech(payload: dict):
    text = payload.get("text", "").strip()
    voice = payload.get("voice", "BV074_streaming")
    rate = payload.get("rate", 1.0)
    pitch = payload.get("pitch", 0)
    need_timestamp = payload.get("need_timestamp", False)
    resource_id = payload.get("resource_id")

    if not text:
        raise HTTPException(status_code=400, detail="Text cannot be empty")

    try:
        chunks = split_text_into_chunks(text, max_chars=4000)
        
        # If single chunk (under 4000 chars), process directly for speed
        if len(chunks) <= 1:
            tts = run_tts_once(text, voice, rate, resource_id, pitch=pitch)
            response_data = {
                "status": "success",
                "speech_url": tts["speech_url"],
                "duration_ms": tts["duration_ms"],
                "text": text,
                "voice": voice,
            }

            if need_timestamp:
                temp_dir = tempfile.mkdtemp()
                try:
                    audio_path = os.path.join(temp_dir, "speech.mp3")
                    download_url_to_file(tts["speech_url"], audio_path, timeout=60)
                    upload_res = main.upload_audio_to_capcut(audio_path, device=DEFAULT_DEVICE)
                    lang_code = guess_stt_lang_from_voice(voice)
                    stt_payload = main.capcut_stt(
                        upload_res["vid"], upload_res["md5"], upload_res["duration_ms"], lang_code
                    )
                    if stt_payload:
                        response_data["srt"] = capcut_to_srt_string(stt_payload)
                        response_data["utterances"] = stt_payload.get("utterances", [])
                    else:
                        response_data["srt"] = ""
                        response_data["utterances"] = []
                except Exception as se:
                    print(f"Error during timestamp STT generation: {se}")
                    response_data["srt"] = ""
                    response_data["utterances"] = []
                    response_data["stt_error"] = str(se)
                finally:
                    shutil.rmtree(temp_dir, ignore_errors=True)

            return JSONResponse(content=response_data)

        # Multi-chunk processing (> 4000 chars): run TTS chunk by chunk and concatenate
        temp_dir = tempfile.mkdtemp(prefix="long_tts_")
        try:
            mp3_files = []
            srt_blocks = []
            cursor_ms = 0

            for idx, chunk in enumerate(chunks):
                tts_res = run_tts_once(chunk, voice, rate, resource_id, pitch=pitch)
                chunk_mp3 = os.path.join(temp_dir, f"chunk_{idx:03d}.mp3")
                download_url_to_file(tts_res["speech_url"], chunk_mp3)

                dur_ms = int(tts_res.get("duration_ms") or 0)
                if dur_ms <= 0:
                    dur_ms = max(800, int(len(chunk) / 14 * 1000))

                mp3_files.append(chunk_mp3)

                if need_timestamp:
                    srt_body = simple_srt_for_segment(chunk, dur_ms, cursor_ms)
                    srt_blocks.append(srt_body)

                cursor_ms += dur_ms + 150

            out_filename = f"long_tts_{uuid.uuid4().hex[:8]}.mp3"
            static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "downloads")
            os.makedirs(static_dir, exist_ok=True)
            out_mp3_path = os.path.join(static_dir, out_filename)

            ffmpeg_concat_mp3(mp3_files, out_mp3_path, gap_ms=150)
            combined_srt = "\n\n".join(b.strip() for b in srt_blocks if b.strip())

            return JSONResponse(content={
                "status": "success",
                "speech_url": f"/static/downloads/{out_filename}",
                "duration_ms": cursor_ms,
                "text": text,
                "voice": voice,
                "chunks_count": len(chunks),
                "srt": combined_srt if need_timestamp else ""
            })
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    except TimeoutError as e:
        raise HTTPException(status_code=504, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/tts-dialogue")
async def tts_dialogue(payload: dict):
    """
    Process dual-voice dialogue script.
    Extract dialogue turns, automatically drop speaker names (e.g. 'Hùng:', 'Lan:'),
    run TTS for each turn using assigned voice, concatenate audio MP3s and merge SRTs.
    """
    text = payload.get("text", "").strip()
    char1_name = payload.get("char1_name", "").strip().lower()
    char1_voice = payload.get("char1_voice", "BV074_streaming")
    char2_name = payload.get("char2_name", "").strip().lower()
    char2_voice = payload.get("char2_voice", "BV074_streaming")
    rate = payload.get("rate", 1.0)
    pitch = payload.get("pitch", 0)
    need_timestamp = payload.get("need_timestamp", False)

    if not text:
        raise HTTPException(status_code=400, detail="Văn bản không được để trống")

    # Split lines and parse dialogue turns
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    dialogue_turns = []

    # Default fallback voice if speaker name doesn't match char1 or char2
    current_voice = char1_voice
    
    for line in lines:
        matched_speaker = None
        speech_text = line

        # Match format: "Name: Text" or "Name：Text"
        if ":" in line or "：" in line:
            parts = re.split(r"[:：]", line, maxsplit=1)
            speaker_prefix = parts[0].strip().lower()
            content = parts[1].strip()

            if char1_name and (speaker_prefix == char1_name or char1_name in speaker_prefix):
                current_voice = char1_voice
                speech_text = content
                matched_speaker = char1_name
            elif char2_name and (speaker_prefix == char2_name or char2_name in speaker_prefix):
                current_voice = char2_voice
                speech_text = content
                matched_speaker = char2_name
            else:
                speech_text = content
        
        if speech_text:
            dialogue_turns.append({
                "voice": current_voice,
                "text": speech_text,
                "speaker": matched_speaker
            })

    # If no explicit "Name: Text" tags matched, alternate lines between char1 and char2
    if len(dialogue_turns) > 1 and not any(t["speaker"] for t in dialogue_turns):
        for idx, turn in enumerate(dialogue_turns):
            turn["voice"] = char1_voice if (idx % 2 == 0) else char2_voice

    if not dialogue_turns:
        raise HTTPException(status_code=400, detail="Kịch bản đối thoại trống, vui lòng nhập nội dung!")

    temp_dir = tempfile.mkdtemp(prefix="dialogue_tts_")
    try:
        mp3_files = []
        srt_blocks = []
        cursor_ms = 0

        for idx, turn in enumerate(dialogue_turns):
            turn_text = turn["text"]
            turn_voice = turn["voice"]
            
            # Generate TTS for turn
            tts_res = run_tts_once(turn_text, turn_voice, rate=rate, pitch=pitch)
            turn_mp3 = os.path.join(temp_dir, f"turn_{idx:03d}.mp3")
            download_url_to_file(tts_res["speech_url"], turn_mp3)
            
            dur_ms = int(tts_res.get("duration_ms") or 0)
            if dur_ms <= 0:
                dur_ms = max(800, int(len(turn_text) / 14 * 1000))

            mp3_files.append(turn_mp3)

            # Generate SRT block for turn
            srt_body = simple_srt_for_segment(turn_text, dur_ms, cursor_ms)
            srt_blocks.append(srt_body)

            # Advance cursor with 200ms gap
            cursor_ms += dur_ms + 200

        # Save concatenated audio output into static/downloads or temp response
        out_filename = f"dialogue_{uuid.uuid4().hex[:8]}.mp3"
        static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "downloads")
        os.makedirs(static_dir, exist_ok=True)
        out_mp3_path = os.path.join(static_dir, out_filename)

        ffmpeg_concat_mp3(mp3_files, out_mp3_path, gap_ms=200)

        combined_srt = "\n\n".join(b.strip() for b in srt_blocks if b.strip())

        return JSONResponse(content={
            "status": "success",
            "speech_url": f"/static/downloads/{out_filename}",
            "duration_ms": cursor_ms,
            "text": text,
            "srt": combined_srt if need_timestamp else "",
            "turn_count": len(dialogue_turns)
        })

    except Exception as e:
        print(f"Error rendering dialogue TTS: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)



# =============================================================
# SCRIPT → MULTI-SCENE TTS (batch for video VO)
# =============================================================
@app.post("/api/script/preview")
async def preview_script_scenes(payload: dict):
    """Parse script into scenes + TTS segments (no CapCut calls)."""
    script = payload.get("script", "")
    mode = payload.get("split_mode", "auto")
    max_chars = int(payload.get("max_chars", 400) or 400)
    scenes = parse_script_scenes(script, mode=mode)
    segments = expand_scenes_with_splits(scenes, max_chars=max_chars)
    return JSONResponse(
        content={
            "status": "success",
            "scene_count": len(scenes),
            "segment_count": len(segments),
            "total_chars": sum(s.get("char_count", 0) for s in segments),
            "scenes": scenes,
            "segments": segments,
        }
    )


def _script_job_log(task_id: str, msg: str):
    job = script_jobs.get(task_id)
    if not job:
        return
    t_str = time.strftime("%H:%M:%S")
    line = f"[{t_str}] {msg}"
    job["logs"].append(line)
    try:
        print(f"[script:{task_id[:8]}] {line}")
    except Exception:
        pass


def run_script_render_job(task_id: str, options: dict):
    job = script_jobs[task_id]
    job["status"] = "processing"
    temp_dir = tempfile.mkdtemp(prefix="script_tts_")
    job["temp_dir"] = temp_dir
    try:
        script = options.get("script") or ""
        voice = options.get("voice") or "BV074_streaming"
        rate = options.get("rate", 1.0)
        split_mode = options.get("split_mode", "auto")
        max_chars = int(options.get("max_chars", 400) or 400)
        gap_ms = int(options.get("gap_ms", 300) or 0)
        need_timestamp = bool(options.get("need_timestamp", False))
        project_name = sanitize_filename(options.get("project_name") or "script_project")

        _script_job_log(task_id, "Phân tích kịch bản...")
        scenes = parse_script_scenes(script, mode=split_mode)
        segments = expand_scenes_with_splits(scenes, max_chars=max_chars)
        if not segments:
            raise ValueError("Không có đoạn nào để render. Kiểm tra kịch bản.")

        job["total"] = len(segments)
        job["done"] = 0
        _script_job_log(task_id, f"Có {len(scenes)} cảnh → {len(segments)} đoạn TTS (max {max_chars} ký tự/đoạn)")

        seg_dir = os.path.join(temp_dir, "segments")
        full_dir = os.path.join(temp_dir, "full")
        os.makedirs(seg_dir, exist_ok=True)
        os.makedirs(full_dir, exist_ok=True)

        audio_paths = []
        srt_pairs = []  # (relative_srt, offset_ms)
        cursor_ms = 0
        meta_segments = []

        for seg in segments:
            idx = seg["index"]
            title = seg.get("title") or f"segment_{idx}"
            text = seg["text"]
            prefix = f"{idx:02d}_{sanitize_filename(title)}"
            _script_job_log(task_id, f"[{idx}/{len(segments)}] TTS: {title[:50]} ({len(text)} ký tự)")

            try:
                tts = run_tts_once(text, voice, rate)
                mp3_path = os.path.join(seg_dir, f"{prefix}.mp3")
                download_url_to_file(tts["speech_url"], mp3_path)
                duration_ms = int(tts.get("duration_ms") or 0)
                if duration_ms <= 0:
                    # rough estimate ~14 chars/sec Vietnamese
                    duration_ms = max(800, int(len(text) / 14 * 1000))

                # SRT: STT timestamps optional; default simple block
                srt_body = ""
                if need_timestamp:
                    try:
                        upload_res = main.upload_audio_to_capcut(mp3_path, device=DEFAULT_DEVICE)
                        stt_payload = main.capcut_stt(
                            upload_res["vid"],
                            upload_res["md5"],
                            upload_res["duration_ms"] or duration_ms,
                            guess_stt_lang_from_voice(voice),
                        )
                        if stt_payload:
                            srt_body = capcut_to_srt_string(stt_payload)
                    except Exception as se:
                        _script_job_log(task_id, f"   ⚠️ STT timestamp fail, dùng SRT đơn: {se}")
                if not srt_body.strip():
                    srt_body = simple_srt_for_segment(text, duration_ms, 0)

                srt_path = os.path.join(seg_dir, f"{prefix}.srt")
                txt_path = os.path.join(seg_dir, f"{prefix}.txt")
                with open(srt_path, "w", encoding="utf-8") as fp:
                    fp.write(srt_body if srt_body.endswith("\n") else srt_body + "\n")
                with open(txt_path, "w", encoding="utf-8") as fp:
                    fp.write(text + "\n")

                audio_paths.append(mp3_path)
                srt_pairs.append((srt_body, cursor_ms))
                meta_segments.append(
                    {
                        "index": idx,
                        "title": title,
                        "text": text,
                        "file_mp3": f"segments/{prefix}.mp3",
                        "file_srt": f"segments/{prefix}.srt",
                        "duration_ms": duration_ms,
                        "start_ms": cursor_ms,
                        "speech_url": tts["speech_url"],
                    }
                )
                cursor_ms += duration_ms + max(0, gap_ms)
                job["done"] = idx
                _script_job_log(task_id, f"   ✅ xong ({duration_ms} ms)")
            except Exception as ex:
                _script_job_log(task_id, f"   ❌ Lỗi đoạn {idx}: {ex}")
                job["errors"].append({"index": idx, "title": title, "error": str(ex)})
                # continue other segments
                continue

        if not audio_paths:
            raise RuntimeError("Không đoạn nào TTS thành công")

        # Write script + meta
        with open(os.path.join(temp_dir, "script.txt"), "w", encoding="utf-8") as fp:
            fp.write(script)
        merged_srt = merge_srt_files(srt_pairs)
        with open(os.path.join(full_dir, "voiceover.srt"), "w", encoding="utf-8") as fp:
            fp.write(merged_srt)

        full_mp3 = os.path.join(full_dir, "voiceover.mp3")
        try:
            _script_job_log(task_id, "Nối audio bằng ffmpeg...")
            ffmpeg_concat_mp3(audio_paths, full_mp3, gap_ms=gap_ms)
            _script_job_log(task_id, "✅ Đã tạo full/voiceover.mp3")
        except Exception as fe:
            _script_job_log(task_id, f"⚠️ Không nối được full mp3 (ffmpeg): {fe}")

        meta = {
            "project_name": project_name,
            "voice": voice,
            "rate": rate,
            "split_mode": split_mode,
            "max_chars": max_chars,
            "gap_ms": gap_ms,
            "need_timestamp": need_timestamp,
            "scene_count": len(scenes),
            "segment_count": len(segments),
            "success_count": len(meta_segments),
            "total_duration_ms": cursor_ms - (gap_ms if meta_segments else 0),
            "segments": meta_segments,
            "errors": job["errors"],
            "created_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        }
        with open(os.path.join(temp_dir, "meta.json"), "w", encoding="utf-8") as fp:
            json.dump(meta, fp, ensure_ascii=False, indent=2)
            fp.write("\n")

        # Preset snapshot for convenience
        with open(os.path.join(temp_dir, "preset.json"), "w", encoding="utf-8") as fp:
            json.dump(
                {
                    "name": project_name,
                    "voice": voice,
                    "rate": rate,
                    "split_mode": split_mode,
                    "max_chars": max_chars,
                    "gap_ms": gap_ms,
                    "need_timestamp": need_timestamp,
                },
                fp,
                ensure_ascii=False,
                indent=2,
            )
            fp.write("\n")

        zip_path = os.path.join(temp_dir, f"{project_name}.zip")
        _script_job_log(task_id, "Đóng gói ZIP...")
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for root, _, files in os.walk(temp_dir):
                for fn in files:
                    if fn.endswith(".zip"):
                        continue
                    full = os.path.join(root, fn)
                    arc = os.path.relpath(full, temp_dir).replace("\\", "/")
                    zf.write(full, arcname=arc)
        job["zip_path"] = zip_path
        job["status"] = "completed"
        job["meta"] = meta
        _script_job_log(task_id, "🎉 Hoàn tất! Tải ZIP để dùng làm voice-over video.")
    except Exception as e:
        job["status"] = "failed"
        _script_job_log(task_id, f"❌ Lỗi hệ thống: {e}")
        job["error"] = str(e)


@app.post("/api/script/render")
async def start_script_render(payload: dict):
    script = (payload.get("script") or "").strip()
    if not script:
        raise HTTPException(status_code=400, detail="Script cannot be empty")

    voice = payload.get("voice") or "BV074_streaming"
    if voice not in voice_resource_map and not payload.get("resource_id"):
        # still allow — resolve falls back
        pass

    task_id = str(uuid.uuid4())
    script_jobs[task_id] = {
        "status": "queued",
        "logs": [],
        "errors": [],
        "total": 0,
        "done": 0,
        "zip_path": None,
        "temp_dir": None,
        "meta": None,
        "error": None,
    }
    options = {
        "script": script,
        "voice": voice,
        "rate": float(payload.get("rate", 1.0) or 1.0),
        "split_mode": payload.get("split_mode", "auto"),
        "max_chars": int(payload.get("max_chars", 400) or 400),
        "gap_ms": int(payload.get("gap_ms", 300) or 0),
        "need_timestamp": bool(payload.get("need_timestamp", False)),
        "project_name": payload.get("project_name") or "script_project",
        "resource_id": payload.get("resource_id"),
    }
    threading.Thread(target=run_script_render_job, args=(task_id, options), daemon=True).start()
    return {"task_id": task_id}


@app.get("/api/script/progress/{task_id}")
async def script_progress(task_id: str):
    if task_id not in script_jobs:
        raise HTTPException(status_code=404, detail="Task not found")

    def event_generator():
        last_index = 0
        while True:
            job = script_jobs.get(task_id)
            if not job:
                break
            logs = job["logs"]
            while last_index < len(logs):
                yield f"data: {json.dumps({'status': job['status'], 'log': logs[last_index], 'done': job.get('done', 0), 'total': job.get('total', 0)}, ensure_ascii=False)}\n\n"
                last_index += 1
            if job["status"] in ("completed", "failed"):
                payload = {
                    "status": job["status"],
                    "finished": True,
                    "done": job.get("done", 0),
                    "total": job.get("total", 0),
                    "download_url": f"/api/script/download/{task_id}" if job["status"] == "completed" else None,
                    "error": job.get("error"),
                    "meta": job.get("meta"),
                }
                yield f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"
                break
            time.sleep(0.4)

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@app.get("/api/script/download/{task_id}")
async def script_download(task_id: str, background_tasks: BackgroundTasks):
    job = script_jobs.get(task_id)
    if not job or not job.get("zip_path") or not os.path.exists(job["zip_path"]):
        raise HTTPException(status_code=404, detail="Zip not found or task not completed")
    zip_path = job["zip_path"]
    name = "script_tts_project.zip"
    try:
        meta = job.get("meta") or {}
        if meta.get("project_name"):
            name = f"{sanitize_filename(meta['project_name'])}.zip"
    except Exception:
        pass

    def _cleanup():
        # keep zip readable during response; cleanup temp after a delay is hard —
        # delete whole temp on next startup is fine. Optional delayed cleanup:
        try:
            # don't delete immediately — FileResponse may still stream
            pass
        except Exception:
            pass

    background_tasks.add_task(_cleanup)
    return FileResponse(zip_path, filename=name, media_type="application/zip")


def extract_or_compress_audio_for_stt(input_path: str, suffix: str) -> tuple[str, bool]:
    """
    Extract or compress audio to lightweight MP3 (mono, 16kHz, 64kbps) if file is video or large.
    Returns (path_to_use, is_temp_created).
    """
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        return input_path, False

    video_exts = {".mp4", ".mov", ".avi", ".mkv", ".webm", ".flv", ".wmv", ".m4v"}
    file_size = os.path.getsize(input_path) if os.path.exists(input_path) else 0
    is_video = suffix.lower() in video_exts

    # If it's a video file or audio larger than 15MB, convert/extract audio stream
    if is_video or file_size > 15 * 1024 * 1024:
        out_temp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        out_temp_path = out_temp.name
        out_temp.close()
        try:
            cmd = [
                ffmpeg, "-y", "-i", input_path,
                "-vn", "-ac", "1", "-ar", "16000", "-b:a", "64k",
                out_temp_path
            ]
            res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if res.returncode == 0 and os.path.exists(out_temp_path) and os.path.getsize(out_temp_path) > 0:
                print(f"[STT Audio Extraction] Converted {file_size / (1024*1024):.2f}MB ({suffix}) -> {os.path.getsize(out_temp_path) / (1024*1024):.2f}MB (mp3 16kHz mono)")
                return out_temp_path, True
            else:
                if os.path.exists(out_temp_path):
                    os.remove(out_temp_path)
        except Exception as e:
            print(f"[STT Audio Extraction Error]: {e}")
            if os.path.exists(out_temp_path):
                os.remove(out_temp_path)

    return input_path, False


@app.post("/api/stt")
async def speech_to_text(
    file: UploadFile = File(...),
    language: str = Form("auto"),
    txt_style: str = Form("start"),
    merge_cues: str = Form("true"),
    max_gap_ms: int = Form(450),
    max_chars: int = Form(100),
):
    """
    Upload audio/video → CapCut STT → SRT + timestamped TXT (one sentence per line).

    merge_cues: gộp cue ngắn liền kề (vd: "em chỗ mua cái" + "váy này")
    max_gap_ms / max_chars: ngưỡng gộp
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="Missing file name")

    # Prefer audio containers for this feature; video still accepted
    suffix = os.path.splitext(file.filename)[1].lower() or ".mp3"
    allowed = {".mp3", ".wav", ".m4a", ".mp4", ".aac", ".flac", ".ogg", ".webm", ".mov", ".avi", ".mkv"}
    if suffix not in allowed:
        raise HTTPException(
            status_code=400,
            detail=f"Định dạng không hỗ trợ ({suffix}). Dùng mp3, wav, m4a, mp4, mov, avi, mkv...",
        )

    style = (txt_style or "start").lower().strip()
    if style not in ("start", "range", "plain", "srt_line", "srt_block", "no_timestamp", "none", "text_only", "no_ts", "raw"):
        style = "start"

    merge = str(merge_cues).strip().lower() in ("1", "true", "yes", "on")
    try:
        gap = int(max_gap_ms)
    except (TypeError, ValueError):
        gap = 450
    try:
        mchars = int(max_chars)
    except (TypeError, ValueError):
        mchars = 100

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp:
        try:
            shutil.copyfileobj(file.file, temp)
            temp_path = temp.name
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to write uploaded file: {e}")

    converted_path = None
    try:
        # Pre-process: extract audio if video or compress if large audio
        upload_path, is_converted = extract_or_compress_audio_for_stt(temp_path, suffix)
        if is_converted:
            converted_path = upload_path

        print(f"Uploading file {file.filename} to CapCut (using {upload_path})...")
        up_info = main.upload_audio_to_capcut(upload_path)
        print("Upload complete:", up_info)

        print(f"Triggering STT recognition in language: {language}...")
        stt_json = main.capcut_stt(
            up_info["vid"],
            up_info["md5"],
            up_info["duration_ms"],
            language,
        )

        if not stt_json:
            raise HTTPException(status_code=500, detail="Speech-to-Text task failed or timed out")

        raw_count = len((stt_json or {}).get("utterances") or [])
        srt_content = capcut_to_srt_string(
            stt_json, merge=merge, max_gap_ms=gap, max_chars=mchars
        )
        timestamped_txt, lines = utterances_to_timestamped_txt(
            stt_json,
            style=style,
            merge=merge,
            max_gap_ms=gap,
            max_chars=mchars,
        )

        return {
            "status": "success",
            "vid": up_info["vid"],
            "duration_ms": up_info["duration_ms"],
            "subtitles_raw": stt_json,
            "srt": srt_content,
            "timestamped_txt": timestamped_txt,
            "txt_style": style,
            "merge_cues": merge,
            "max_gap_ms": gap,
            "max_chars": mchars,
            "lines": lines,
            "line_count": len(lines),
            "raw_utterance_count": raw_count,
            "source_filename": file.filename,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        if converted_path and os.path.exists(converted_path):
            os.remove(converted_path)

# =============================================================
# TIKTOK SCRAPER & TRANSCRIPTION SERVICES
# =============================================================
active_tasks = {}

def require_yt_dlp():
    if yt_dlp is None:
        raise RuntimeError("yt-dlp chưa được cài. Chạy: pip install yt-dlp")

def run_tiktok_scraper(
    task_id: str,
    channel_url: str,
    language: str,
    limit: int,
    limit_mode: str = "latest",
    min_views: int = 0,
    min_likes: int = 0,
    min_duration: int = 0,
    max_duration: int = 0,
    playlist_url: str = ""
):
    active_tasks[task_id] = {
        "status": "processing",
        "logs": [],
        "zip_path": None,
        "temp_dir": None
    }
    
    def log(msg):
        t_str = time.strftime("%H:%M:%S")
        formatted = f"[{t_str}] {msg}"
        active_tasks[task_id]["logs"].append(formatted)
        try:
            print(f"[{task_id}] {formatted}")
        except Exception:
            try:
                print(f"[{task_id}] {formatted.encode('ascii', 'replace').decode('ascii')}")
            except Exception:
                pass

    try:
        require_yt_dlp()
        log("Bắt đầu khởi chạy cào kênh TikTok...")
        temp_dir = tempfile.mkdtemp()
        active_tasks[task_id]["temp_dir"] = temp_dir
        
        # 1. Extract list of videos in channel (flat mode)
        flat_opts = {
            'extract_flat': True,
            'playlistend': limit if limit_mode == "latest" else None,
            'quiet': True,
            'no_warnings': True
        }
        
        source_url = sanitize_tiktok_url(playlist_url) if playlist_url and playlist_url.strip() else sanitize_tiktok_url(channel_url)
        log(f"Đang phân tích nguồn: {source_url}")
        
        entries = []
        if "/collection/" in source_url:
            log("Phát hiện nguồn là Danh sách phát/Bộ sưu tập. Bắt đầu dùng Playwright để quét danh sách video...")
            import asyncio
            try:
                try:
                    loop = asyncio.get_event_loop()
                except RuntimeError:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                entries = loop.run_until_complete(scrape_tiktok_playlist_videos(source_url, log))
            except Exception as pe:
                raise ValueError(f"Lỗi khi quét danh sách phát bằng Playwright: {pe}")
        else:
            with yt_dlp.YoutubeDL(flat_opts) as ydl:
                try:
                    info = ydl.extract_info(source_url, download=False)
                except Exception as e:
                    raise ValueError(f"yt-dlp không thể đọc nguồn: {e}")
                    
                if not info:
                    raise ValueError("Không tìm thấy thông tin nguồn.")
                    
                if 'entries' in info:
                    entries = [e for e in info['entries'] if e]
                else:
                    entries = [info]
                
        # Apply filters
        filtered = []
        for e in entries:
            dur = e.get("duration") or 0
            views = e.get("view_count") or 0
            likes = e.get("like_count") or 0
            
            if min_views and views < min_views:
                continue
            if min_likes and likes < min_likes:
                continue
            if min_duration and dur < min_duration:
                continue
            if max_duration and dur > max_duration:
                continue
            filtered.append(e)
        
        entries = filtered
        
        # Slice only if limit_mode is latest
        if limit_mode == "latest":
            entries = entries[:limit]
            
        if not entries:
            raise ValueError("Không tìm thấy video nào phù hợp với bộ lọc trên kênh.")
            
        log(f"Đã tìm thấy {len(entries)} video phù hợp. Bắt đầu xử lý từng video...")
        
        md_files = []
        for idx, entry in enumerate(entries, 1):
            title = entry.get('title') or f"video_{idx}"
            video_url = entry.get('webpage_url') or entry.get('url') or ""
            desc = entry.get('description') or ""
            
            if not video_url:
                log(f"[{idx}/{len(entries)}] ⚠️ Bỏ qua video không có URL: \"{title}\"")
                continue
                
            log(f"[{idx}/{len(entries)}] Đang xử lý: \"{title}\"")
            log(f"   📥 Đang tải xuống âm thanh...")
            
            # Download audio for this single video
            single_opts = {
                'format': 'ba[ext=m4a]/ba/best[vcodec*=h264]/best',
                'outtmpl': os.path.join(temp_dir, f'video_{idx}_%(title)s.%(ext)s'),
                'quiet': True,
                'no_warnings': True
            }
            
            audio_path = None
            with yt_dlp.YoutubeDL(single_opts) as ydl_single:
                try:
                    single_info = ydl_single.extract_info(video_url, download=True)
                    if single_info:
                        audio_path = ydl_single.prepare_filename(single_info)
                except Exception as de:
                    log(f"   ⚠️ Lỗi tải âm thanh: {de}. Thử định dạng khác...")
                    # Fallback try any audio
                    try:
                        fallback_opts = {
                            'format': 'ba/best[vcodec*=h264]/best',
                            'outtmpl': os.path.join(temp_dir, f'video_{idx}_%(title)s.%(ext)s'),
                            'quiet': True,
                            'no_warnings': True
                        }
                        with yt_dlp.YoutubeDL(fallback_opts) as ydl_fb:
                            fb_info = ydl_fb.extract_info(video_url, download=True)
                            if fb_info:
                                audio_path = ydl_fb.prepare_filename(fb_info)
                    except Exception as fe:
                        log(f"   ❌ Không thể tải video: {fe}")
                        continue

            # Verify file exists
            if not audio_path or not os.path.exists(audio_path):
                # Try scanning the folder for video_{idx}_ prefix in case filename template differed
                scanned_path = None
                for fname in os.listdir(temp_dir):
                    if fname.startswith(f"video_{idx}_") and fname.endswith(('.m4a', '.webm', '.mp3', '.mp4', '.ogg', '.wav')):
                        scanned_path = os.path.join(temp_dir, fname)
                        break
                if scanned_path:
                    audio_path = scanned_path
                else:
                    log(f"   ⚠️ Không tìm thấy file âm thanh đã tải xuống. Bỏ qua.")
                    continue
                
            # Extract audio using ffmpeg if it's a video file container
            ext = os.path.splitext(audio_path)[1].lower()
            if ext in ('.mp4', '.webm', '.ogg'):
                log(f"   🎬 Phát hiện file video ({ext}). Đang trích xuất audio bằng FFmpeg...")
                clean_audio_path = os.path.splitext(audio_path)[0] + "_extracted.m4a"
                
                success = False
                try:
                    cmd = ["ffmpeg", "-y", "-i", audio_path, "-vn", "-c:a", "copy", clean_audio_path]
                    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    if res.returncode == 0 and os.path.exists(clean_audio_path) and os.path.getsize(clean_audio_path) > 0:
                        success = True
                    else:
                        log(f"   ⚠️ FFmpeg copy failed (code {res.returncode}): {res.stderr.decode('utf-8', errors='ignore')}")
                except Exception as e:
                    log(f"   ⚠️ Exception in FFmpeg copy: {e}")
                    
                if not success:
                    try:
                        cmd = ["ffmpeg", "-y", "-i", audio_path, "-vn", "-c:a", "aac", "-b:a", "128k", clean_audio_path]
                        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        if res.returncode == 0 and os.path.exists(clean_audio_path) and os.path.getsize(clean_audio_path) > 0:
                            success = True
                        else:
                            log(f"   ⚠️ FFmpeg re-encode failed (code {res.returncode}): {res.stderr.decode('utf-8', errors='ignore')}")
                    except Exception as e:
                        log(f"   ⚠️ Exception in FFmpeg re-encode: {e}")
                        
                if success:
                    log(f"   ✅ Đã trích xuất xong audio stream.")
                    audio_path = clean_audio_path
                else:
                    log(f"   ⚠️ Không thể trích xuất audio bằng FFmpeg. Thử tải file gốc lên...")
                
            log(f"   🚀 Đang upload audio lên máy chủ CapCut...")
            try:
                up_info = main.upload_audio_to_capcut(audio_path)
                log(f"   ⏳ Đang gửi yêu cầu bóc băng chữ ký bảo mật...")
                stt_json = main.capcut_stt(
                    up_info["vid"],
                    up_info["md5"],
                    up_info["duration_ms"],
                    language
                )
                
                if not stt_json:
                    log(f"   ❌ CapCut API không phản hồi hoặc hết hạn task.")
                    continue
                    
                paragraphs = []
                for utt in stt_json.get("utterances", []):
                    text = utt.get("text", "").strip()
                    if text:
                        paragraphs.append(text)
                script_text = " ".join(paragraphs)
                
                clean_title = re.sub(r'[\\/*?:"<>|]', "", title)[:100].strip() or f"video_{idx}"
                md_content = f"# {title}\n\n- **Đường dẫn video**: {video_url}\n- **Mô tả**: {desc}\n\n---\n\n## 📝 Lời thoại kịch bản:\n\n{script_text}\n"
                md_files.append((f"{clean_title}.md", md_content))
                log(f"   ✅ Trích xuất kịch bản thành công.")
            except Exception as ex:
                log(f"   ❌ Lỗi khi bóc băng: {ex}")
                
        if not md_files:
            raise ValueError("Không có video nào được bóc băng thành công!")
            
        zip_path = os.path.join(temp_dir, f"tiktok_transcripts_{task_id}.zip")
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for filename, content in md_files:
                zipf.writestr(filename, content)
                
        active_tasks[task_id]["zip_path"] = zip_path
        active_tasks[task_id]["status"] = "completed"
        log("🎉 Đã bóc băng xong toàn bộ video và đóng gói ZIP thành công!")
            
    except Exception as e:
        log(f"❌ Lỗi hệ thống: {str(e)}")
        active_tasks[task_id]["status"] = "failed"

async def scrape_tiktok_playlist_videos(playlist_url: str, log_func = None):
    # For Playwright browser navigation, /playlist/ is required (not /collection/)
    if "/collection/" in playlist_url:
        playlist_url = playlist_url.replace("/collection/", "/playlist/")

    def debug_log(msg):
        if log_func:
            log_func(msg)
        else:
            print(msg)

    import asyncio
    try:
        from playwright.async_api import async_playwright
    except ImportError:
        raise RuntimeError("Thư viện playwright chưa được cài đặt trên server.")

    videos = []
    seen_ids = set()

    debug_log("Khởi động trình duyệt Playwright headless...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            locale="en-US"
        )
        page = await context.new_page()

        async def handle_response(response):
            if "/api/mix/item_list/" in response.url:
                try:
                    text = await response.text()
                    data = json.loads(text)
                    items = data.get("itemList", [])
                    debug_log(f"Đã phát hiện API và lấy được {len(items)} video.")
                    for item in items:
                        vid_id = item.get("id")
                        if vid_id and vid_id not in seen_ids:
                            seen_ids.add(vid_id)
                            author = item.get("author", {})
                            username = author.get("uniqueId") or ""
                            video = item.get("video", {})
                            stats = item.get("stats", {})
                            videos.append({
                                "id": vid_id,
                                "url": f"https://www.tiktok.com/@{username}/video/{vid_id}" if username else "",
                                "title": item.get("desc") or f"video_{vid_id}",
                                "description": item.get("desc") or "",
                                "duration": video.get("duration") or 0,
                                "view_count": stats.get("playCount") or 0,
                                "like_count": stats.get("diggCount") or 0,
                                "comment_count": stats.get("commentCount") or 0,
                                "repost_count": stats.get("shareCount") or 0,
                                "timestamp": item.get("createTime") or 0
                            })
                except Exception as e:
                    debug_log(f"Lỗi khi đọc phản hồi từ API: {e}")

        page.on("response", handle_response)

        try:
            debug_log(f"Đang tải trang danh sách phát: {playlist_url}")
            await page.goto(playlist_url, wait_until="networkidle", timeout=15000)
            await asyncio.sleep(3)

            # Scroll multiple times to trigger pagination
            for i in range(5):
                debug_log(f"Cuộn trang lần {i+1}/5...")
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await page.evaluate("""
                    () => {
                        const containers = document.querySelectorAll('[class*="DivListInnerContainer"], [class*="DivDraggableListContainer"]');
                        containers.forEach(c => {
                            c.scrollTop = c.scrollHeight;
                        });
                        const elements = document.querySelectorAll('*');
                        for (const el of elements) {
                            if (el.scrollHeight > el.clientHeight) {
                                el.scrollTop = el.scrollHeight;
                            }
                        }
                    }
                """)
                await asyncio.sleep(2)

        except Exception as e:
            debug_log(f"Lỗi trong quá trình cuộn trang: {e}")

        # Fallback to HTML rehydration state if no videos collected from network interception
        if not videos:
            debug_log("Không thu thập được video nào từ API. Bắt đầu phân tích trạng thái HTML rehydration làm dự phòng...")
            try:
                html = await page.content()
                
                univer = re.search(r'<script id="__UNIVERSAL_DATA_FOR_REHYDRATION__" type="application/json">(.*?)</script>', html)
                sigi = re.search(r'<script id="SIGI_STATE" type="application/json">(.*?)</script>', html)
                
                data_json = None
                if sigi:
                    data_json = json.loads(sigi.group(1))
                elif univer:
                    data_json = json.loads(univer.group(1))
                    
                if data_json:
                    found_items = []
                    def search_videos(d):
                        if isinstance(d, dict):
                            if "id" in d and "desc" in d and ("video" in d or "author" in d):
                                found_items.append(d)
                            else:
                                for k, v in d.items():
                                    search_videos(v)
                        elif isinstance(d, list):
                            for item in d:
                                search_videos(item)
                    
                    search_videos(data_json)
                    debug_log(f"Tìm thấy {len(found_items)} đối tượng video trong JSON rehydration.")
                    
                    for item in found_items:
                        vid_id = item.get("id")
                        if vid_id and vid_id not in seen_ids:
                            if not re.match(r'^\d{15,25}$', str(vid_id)):
                                continue
                            seen_ids.add(vid_id)
                            author = item.get("author", {})
                            username = author.get("uniqueId") or ""
                            video = item.get("video", {})
                            stats = item.get("stats", {})
                            videos.append({
                                "id": vid_id,
                                "url": f"https://www.tiktok.com/@{username}/video/{vid_id}" if username else "",
                                "title": item.get("desc") or f"video_{vid_id}",
                                "description": item.get("desc") or "",
                                "duration": video.get("duration") or 0,
                                "view_count": stats.get("playCount") or 0,
                                "like_count": stats.get("diggCount") or 0,
                                "comment_count": stats.get("commentCount") or 0,
                                "repost_count": stats.get("shareCount") or 0,
                                "timestamp": item.get("createTime") or 0
                            })
            except Exception as e:
                debug_log(f"Lỗi khi parse rehydration state: {e}")

        # Secondary fallback: Extract standard anchor links matching /video/ if still empty
        if not videos:
            debug_log("Vẫn không tìm thấy video. Thử trích xuất các liên kết /video/ trực tiếp từ DOM...")
            try:
                links = await page.eval_on_selector_all("a", "elements => elements.map(e => ({href: e.href, text: e.textContent}))")
                for l in links:
                    href = l.get("href") or ""
                    text = l.get("text") or ""
                    if "/video/" in href:
                        clean_url = href.split("?")[0]
                        vid_id = clean_url.split("/")[-1]
                        if vid_id and vid_id not in seen_ids and re.match(r'^\d+$', vid_id):
                            seen_ids.add(vid_id)
                            videos.append({
                                "id": vid_id,
                                "url": clean_url,
                                "title": text.strip() or f"video_{vid_id}",
                                "description": text.strip() or "",
                                "duration": 0,
                                "view_count": 0,
                                "like_count": 0,
                                "comment_count": 0,
                                "repost_count": 0,
                                "timestamp": 0
                            })
                debug_log(f"Đã trích xuất được {len(videos)} liên kết video từ DOM.")
            except Exception as e:
                debug_log(f"Lỗi khi trích xuất liên kết từ DOM: {e}")

        await browser.close()
        
    debug_log(f"Kết thúc quét danh sách phát. Tổng cộng thu thập được: {len(videos)} video.")
    return videos

@app.post("/api/tiktok/list")
async def list_tiktok_videos(payload: dict):
    channel_url = payload.get("channel_url", "").strip()
    playlist_url = payload.get("playlist_url", "").strip()
    
    target_url = playlist_url if playlist_url else channel_url
    if not target_url:
        raise HTTPException(status_code=400, detail="Channel URL or Playlist URL is required")
        
    target_url = sanitize_tiktok_url(target_url)
    
    if "/collection/" in target_url:
        try:
            result_list = await scrape_tiktok_playlist_videos(target_url)
            return JSONResponse(content={"status": "success", "videos": result_list})
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Lỗi khi cào danh sách phát bằng Playwright: {str(e)}")

    try:
        require_yt_dlp()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
            
    flat_opts = {
        'extract_flat': True,
        'quiet': True,
        'no_warnings': True
    }
    
    try:
        with yt_dlp.YoutubeDL(flat_opts) as ydl:
            info = ydl.extract_info(target_url, download=False)
            if not info:
                raise HTTPException(status_code=404, detail="Không tìm thấy thông tin nguồn")
                
            entries = []
            if 'entries' in info:
                entries = [e for e in info['entries'] if e]
            else:
                entries = [info]
                
            result_list = []
            for e in entries:
                result_list.append({
                    "id": e.get("id"),
                    "url": e.get("webpage_url") or e.get("url") or "",
                    "title": e.get("title") or "",
                    "description": e.get("description") or "",
                    "duration": e.get("duration") or 0,
                    "view_count": e.get("view_count") or 0,
                    "like_count": e.get("like_count") or 0,
                    "comment_count": e.get("comment_count") or 0,
                    "repost_count": e.get("repost_count") or 0,
                    "timestamp": e.get("timestamp") or 0
                })
            return JSONResponse(content={"status": "success", "videos": result_list})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi cào danh sách video: {str(e)}")

@app.post("/api/tiktok/playlists")
async def list_channel_playlists(payload: dict):
    channel_url = payload.get("channel_url", "").strip()
    if not channel_url:
        raise HTTPException(status_code=400, detail="Channel URL is required")
        
    import asyncio
    try:
        from playwright.async_api import async_playwright
    except ImportError:
        raise HTTPException(status_code=500, detail="playwright library is not installed on the server")
        
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                locale="en-US"
            )
            page = await context.new_page()
            await page.goto(channel_url, wait_until="networkidle", timeout=15000)
            await asyncio.sleep(2)
            
            links = await page.eval_on_selector_all("a", "elements => elements.map(e => ({href: e.href, text: e.textContent}))")
            await browser.close()
            
            playlist_list = []
            seen_urls = set()
            for link in links:
                href = link.get("href") or ""
                text = link.get("text") or ""
                if "/playlist/" in href or "/collection/" in href:
                    clean_url = href.split("?")[0]
                    if clean_url in seen_urls:
                        continue
                    seen_urls.add(clean_url)
                    
                    match = re.search(r'^(.*?)(?:\s*|\b)(\d+)\s*(?:posts|video|bài viết|bài đăng|tập|post|videos)\s*$', text, re.IGNORECASE)
                    if match:
                        title = match.group(1).strip()
                        count = int(match.group(2))
                    else:
                        title = text.strip()
                        count = 0
                        
                    playlist_list.append({
                        "title": title or clean_url.split("/")[-1],
                        "url": clean_url,
                        "count": count
                    })
                    
            return JSONResponse(content={"status": "success", "playlists": playlist_list})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi quét danh sách phát: {str(e)}")

@app.post("/api/tiktok/extract")
async def start_tiktok_extraction(payload: dict):
    channel_url = payload.get("channel_url", "").strip()
    playlist_url = payload.get("playlist_url", "").strip()
    language = payload.get("language", "auto")
    limit = int(payload.get("limit", 5))
    limit_mode = payload.get("limit_mode", "latest")
    min_views = int(payload.get("min_views", 0))
    min_likes = int(payload.get("min_likes", 0))
    min_duration = int(payload.get("min_duration", 0))
    max_duration = int(payload.get("max_duration", 0))
    
    if not channel_url and not playlist_url:
        raise HTTPException(status_code=400, detail="Channel URL or Playlist URL is required")
        
    task_id = str(uuid.uuid4())
    threading.Thread(
        target=run_tiktok_scraper,
        args=(task_id, channel_url, language, limit, limit_mode, min_views, min_likes, min_duration, max_duration, playlist_url),
        daemon=True
    ).start()
    
    return {"task_id": task_id}

@app.get("/api/tiktok/progress/{task_id}")
async def get_tiktok_progress(task_id: str):
    if task_id not in active_tasks:
        raise HTTPException(status_code=404, detail="Task not found")
        
    def event_generator():
        last_index = 0
        while True:
            task = active_tasks.get(task_id)
            if not task:
                break
                
            logs = task["logs"]
            while last_index < len(logs):
                yield f"data: {json.dumps({'status': task['status'], 'log': logs[last_index]})}\n\n"
                last_index += 1
                
            if task["status"] in ("completed", "failed"):
                yield f"data: {json.dumps({'status': task['status'], 'done': True, 'download_url': f'/api/tiktok/download/{task_id}' if task['status'] == 'completed' else None})}\n\n"
                break
                
            time.sleep(0.5)
            
    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.get("/api/tiktok/download/{task_id}")
async def download_tiktok_zip(task_id: str):
    task = active_tasks.get(task_id)
    if not task or not task.get("zip_path") or not os.path.exists(task["zip_path"]):
        raise HTTPException(status_code=404, detail="Zip file not found or task not completed")
        
    zip_path = task["zip_path"]
    temp_dir = task["temp_dir"]
    
    from fastapi import BackgroundTasks
    
    def cleanup_temp():
        try:
            shutil.rmtree(temp_dir)
            active_tasks.pop(task_id, None)
            print(f"Cleaned up temp directory and task data for {task_id}")
        except Exception as e:
            print(f"Error cleaning up temp directory: {e}")
            
    bg_tasks = BackgroundTasks()
    bg_tasks.add_task(cleanup_temp)
    
    return FileResponse(zip_path, filename="tiktok_transcripts.zip", background=bg_tasks)

# Serve static directory if it exists
static_dir = os.path.join(BASE_DIR, "static")
os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
