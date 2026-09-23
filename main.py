#!/usr/bin/env python3
import os
import sys
import json
import time
import hashlib
import hmac
import binascii
import uuid
import datetime as dt
from urllib.parse import parse_qsl, quote, urlencode, urlsplit

try:
    import requests
except ImportError:
    sys.exit("Vui lòng mở Terminal/CMD và chạy: pip install requests")

# ==========================================
# CẤU HÌNH CAPCUT API
# ==========================================
BASE = "https://editor-api-sg.capcutapi.com"
VOD_REGION, VOD_SERVICE = "sdwdmwlll", "vod"

DEFAULT_DEVICE = {
    "aid": "359289", "app_name": "CapCut", "appvr": "8.7.0", "version_name": "8.7.0",
    "version_code": "8.7.0", "channel": "capcutpc_google", "device_platform": "mac",
    "device_type": "MacBookPro17,1", "device_brand": "MacBookPro17,1", "os_version": "15.7.4",
    "device_id": "7647183892936328721", "iid": "7647185302080423697", "region": "VN",
    "loc": "VN", "lan": "vi-VN", "pf": "3", "tdid": "7647183892936328721",
}

def compact_json(obj): return json.dumps(obj, ensure_ascii=False, separators=(",", ":"))
def make_x_ss_stub(body_text): return hashlib.md5(body_text.encode("utf-8")).hexdigest()
def sha256_hex(data): return hashlib.sha256(data.encode("utf-8") if isinstance(data, str) else data).hexdigest()
def hmac_sha256(key, msg): return hmac.new(key.encode("utf-8") if isinstance(key, str) else key, msg.encode("utf-8") if isinstance(msg, str) else msg, hashlib.sha256).digest()
def crc32_hex(data): return f"{binascii.crc32(data) & 0xFFFFFFFF:08x}"
def file_md5(path):
    h = hashlib.md5()
    with open(path, "rb") as fp:
        for chunk in iter(lambda: fp.read(1024 * 1024), b""): h.update(chunk)
    return h.hexdigest()

def make_sign_header(url, appvr, device_time, tdid):
    path = url.split("?", 1)[0]
    return hashlib.md5(f"9e2c|{path[-7:]}|3|{appvr}|{device_time}|{tdid}|11ac".encode("utf-8")).hexdigest()

def aws4_authorization(method, url, body, access_key_id, secret_access_key, session_token, amz_date):
    date_stamp = amz_date[:8]
    scope = f"{date_stamp}/{VOD_REGION}/{VOD_SERVICE}/aws4_request"
    signed_headers = "x-amz-date;x-amz-security-token"
    canonical_query = "&".join(quote(str(k), safe="-_.~") + "=" + quote(str(v), safe="-_.~") for k, v in sorted(parse_qsl(urlsplit(url).query, keep_blank_values=True)))
    canonical_request = "\n".join([method, urlsplit(url).path, canonical_query, f"x-amz-date:{amz_date}\nx-amz-security-token:{session_token}\n", signed_headers, sha256_hex(body)])
    string_to_sign = "\n".join(["AWS4-HMAC-SHA256", amz_date, scope, sha256_hex(canonical_request)])
    k_date = hmac_sha256("AWS4" + secret_access_key, date_stamp)
    signature = hmac.new(hmac_sha256(hmac_sha256(hmac_sha256(k_date, VOD_REGION), VOD_SERVICE), "aws4_request"), string_to_sign.encode("utf-8"), hashlib.sha256).hexdigest()
    return f"AWS4-HMAC-SHA256 Credential={access_key_id}/{scope}, SignedHeaders={signed_headers}, Signature={signature}"

def request_capcut_api(path, body, device, appid=False, include_region=True, babi=None):
    now = str(int(time.time()))
    seed = uuid.uuid4().hex[:32]
    body_text = compact_json(body)
    
    q = {k: device[k] for k in ["app_name", "device_type", "os_version", "channel", "version_name", "device_brand", "device_id", "iid", "version_code", "device_platform", "aid"]}
    if include_region: q["region"] = device["region"]
    if babi is not None: q["babi_param"] = compact_json(babi)
    
    url = BASE + path + "?" + urlencode(q)
    headers = {
        "content-type": "application/json", "appvr": device["appvr"], "ch": device["channel"],
        "device-time": now, "lan": device["lan"], "loc": device["loc"], "pf": device["pf"],
        "sign-ver": "1", "tdid": device["tdid"], "x-ss-stub": make_x_ss_stub(body_text),
        "x-ss-dp": device["aid"], "x-khronos": now, "x-tt-trace-id": f"00-{seed}-{seed[:16]}-01",
        "user-agent": "Cronet/TTNetVersion:1d7cc3b1 2025-07-16 QuicVersion:52c2b40d 2025-04-03",
    }
    if appid: headers.update({"app-sdk-version": device["appvr"], "appid": device["aid"]})
    headers["sign"] = make_sign_header(url, device["appvr"], headers["device-time"], device["tdid"])
    
    return url, headers, body_text

# ==========================================
# GIAO TIẾP VỚI CAPCUT (UPLOAD, STT)
# ==========================================
def upload_audio_to_capcut(path, device=DEFAULT_DEVICE):
    local_md5 = file_md5(path)
    with open(path, "rb") as fp: data = fp.read()
    
    url, headers, body = request_capcut_api("/lv/v1/upload_sign", {"biz": "cc_pc_text_recognize", "key_version": "v5"}, device, appid=True, include_region=False)
    creds = requests.post(url, headers=headers, data=body.encode()).json()["data"]
    
    amz_date, http_date = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ"), dt.datetime.now(dt.timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT")
    apply_url = f"https://{creds['domain']}/top/v1?" + urlencode({"Action": "ApplyUploadInner", "SpaceName": creds["space_name"], "UseQuic": "false", "Version": "2020-11-19", "device_platform": "win"})
    vod_headers = {"Authorization": aws4_authorization("GET", apply_url, b"", creds["access_key_id"], creds["secret_access_key"], creds["session_token"], amz_date), "Date": http_date, "X-Amz-Date": amz_date, "X-Amz-Security-Token": creds["session_token"]}
    apply_data = requests.get(apply_url, headers=vod_headers).json()["Result"]["InnerUploadAddress"]["UploadNodes"][0]
    
    upload_host, store_uri, upload_id, upload_auth = apply_data["UploadHost"], apply_data["StoreInfos"][0]["StoreUri"], apply_data["StoreInfos"][0]["UploadID"], apply_data["StoreInfos"][0]["Auth"]
    transfer_url = f"https://{upload_host}/upload/v1/{store_uri}?" + urlencode({"uploadid": upload_id, "part_number": "0", "phase": "transfer"})
    requests.post(transfer_url, headers={"Authorization": upload_auth, "X-Upload-Content-CRC32": crc32_hex(data)}, data=data)
    requests.post(f"https://{upload_host}/upload/v1/{store_uri}?" + urlencode({"uploadmode": "part", "phase": "finish", "uploadid": upload_id}), headers={"Authorization": upload_auth}, data=f"0:{crc32_hex(data)}".encode())
    
    commit_url = f"https://{creds['domain']}/top/v1?" + urlencode({"Action": "CommitUploadInner", "SpaceName": creds["space_name"], "Version": "2020-11-19", "device_platform": "win"})
    commit_body = compact_json({"Functions": [{"Input": {"SnapshotTime": 0.0}, "Name": "Snapshot"}], "SessionKey": apply_data["SessionKey"]})
    amz_date = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    vod_headers.update({"Authorization": aws4_authorization("POST", commit_url, commit_body, creds["access_key_id"], creds["secret_access_key"], creds["session_token"], amz_date), "X-Amz-Date": amz_date})
    commit_data = requests.post(commit_url, headers=vod_headers, data=commit_body.encode()).json()["Result"]["Results"][0]
    
    meta = commit_data.get("VideoMeta", {})
    return {"vid": commit_data.get("Vid"), "md5": meta.get("Md5") or local_md5, "duration_ms": int(float(meta.get("Duration", 0)) * 1000)}

def capcut_stt(vid, md5, duration_ms, lang):
    device = DEFAULT_DEVICE
    babi = {"feature_entrance": "editor", "feature_entrance_detail": "editor-elements-captions-subtitle_recognition", "feature_key": "subtitle_recognition", "scenario": "video_editor"}
    
    # Ép buộc use_translation = False để không bao giờ dịch thuật tự động
    cap_json = {"adjust_endtime": 200, "audio": vid, "audio_type": "vid", "caption_type": 0, "client_request_id": str(uuid.uuid4()), "duration": duration_ms, "enable_cache": True, "enter_from": "asr", "language": lang, "max_lines": 1, "md5": md5, "pack_options": {"need_attribute": True}, "songs_info": [{"end_time": duration_ms - 10.334, "id": "", "start_time": 0}], "translation_language": "vi-VN", "use_translation": False, "words_per_line": 15}
    body = {"bind_id": str(uuid.uuid4()).upper(), "can_queue": True, "enter_from": "asr", "tasks": [{"context": str(uuid.uuid4()), "payload": compact_json({"cap_json": cap_json}), "req_key": "cc_audio_subtitle_asr", "task_version": "v3"}]}
    
    url, headers, b_text = request_capcut_api("/lv/v1/common_task/new", body, device, babi=babi)
    res_new = requests.post(url, headers=headers, data=b_text.encode()).json()
    
    try:
        task_id = res_new["data"]["tasks"][0]["id"]
        token = res_new["data"]["tasks"][0]["token"]
    except KeyError:
        return None
        
    for i in range(150): 
        time.sleep(2)
        q_body = {"tasks": [{"bind_id": "", "id": task_id, "req_key": "cc_audio_subtitle_asr", "task_version": "v3", "token": token}]}
        q_url, q_headers, q_text = request_capcut_api("/lv/v1/common_task/query", q_body, device, include_region=False)
        try:
            q_res = requests.post(q_url, headers=q_headers, data=q_text.encode()).json()
            task_info = q_res["data"]["tasks"][0]
            status = task_info.get("status")
            print(f"STT Query Poll {i+1}: Status = {status}")
            
            if status in ("succeed", 2, "succeeded"):
                payload_str = task_info.get("payload", "{}")
                return json.loads(payload_str)
            elif status in ("failed", "fail", 3):
                print(f"STT Query Failed: {task_info.get('detail_info') or task_info}")
                return None
        except Exception as e:
            print(f"Error querying STT task: {e}")
    return None

# ==========================================
# CÔNG CỤ ĐỊNH DẠNG PHỤ ĐỀ SRT
# ==========================================
def giay_sang_srt(giay):
    h, m, s = int(giay // 3600), int((giay % 3600) // 60), int(giay % 60)
    ms = int(round((giay - int(giay)) * 1000))
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

def json_capcut_to_srt(capcut_json, srt_path):
    try:
        utterances = capcut_json.get("utterances", [])
        
        if not utterances:
            return "NO_SPEECH"
            
        with open(srt_path, "w", encoding="utf-8") as f:
            for i, utt in enumerate(utterances):
                start = float(utt.get("start_time", 0)) / 1000.0
                end = float(utt.get("end_time", 0)) / 1000.0
                
                # Chỉ trích xuất ngôn ngữ gốc, không lấy bản dịch
                text = utt.get("text", "")
                    
                f.write(f"{i+1}\n{giay_sang_srt(start)} --> {giay_sang_srt(end)}\n{text}\n\n")
        return "SUCCESS"
    except Exception as e:
        print(f"❌ Lỗi phân tích JSON từ CapCut: {e}")
        return "ERROR"

# ==========================================
# GIAO DIỆN DÒNG LỆNH (CLI)
# ==========================================
def main_menu():
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print("="*50)
        print("   TOOL TRÍCH XUẤT PHỤ ĐỀ BẰNG AI CAPCUT   ")
        print("="*50)
        print("1. Quét thư mục và xuất phụ đề (.srt) hàng loạt")
        print("0. Thoát")
        print("="*50)
        
        chon = input("Nhập lựa chọn của bạn: ")
        
        if chon == '1':
            print("\n-- CHỌN NGÔN NGỮ GỐC CỦA VIDEO --")
            print("1. Tiếng Việt")
            print("2. Tiếng Trung (Chỉ xuất chữ Hán gốc)")
            print("3. Tiếng Anh (Chỉ xuất tiếng Anh gốc)")
            print("4. Auto phát hiện")
            lang_c = input("Chọn (1-4): ")
            lang_map = {'1': 'vi-VN', '2': 'zh-CN', '3': 'en-US', '4': 'auto'}
            lang = lang_map.get(lang_c, 'auto')
            
            folder_path = input("\nNhập ĐƯỜNG DẪN THƯ MỤC chứa video/audio: ").strip('\"')
            if not os.path.isdir(folder_path):
                input("❌ Đường dẫn thư mục không hợp lệ! Nhấn Enter để quay lại...")
                continue
                
            valid_exts = ('.mp4', '.mp3', '.m4a', '.wav')
            files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.lower().endswith(valid_exts)]
            
            if not files:
                input("❌ Không tìm thấy video/audio nào. Nhấn Enter để quay lại...")
                continue

            print(f"\n🔍 Tìm thấy {len(files)} file. Bắt đầu xử lý hàng loạt...")
            
            so_thanh_cong = 0
            so_bo_qua = 0
            so_khong_loi = 0
            
            for idx, f_path in enumerate(files, 1):
                try:
                    print(f"\n[{idx}/{len(files)}] Đang xử lý file: {os.path.basename(f_path)}")
                    srt_path = os.path.splitext(f_path)[0] + ".srt"
                    
                    if os.path.exists(srt_path):
                        print(f"   ⏭️ Đã có file phụ đề '{os.path.basename(srt_path)}'. Tự động bỏ qua.")
                        so_bo_qua += 1
                        continue
                    
                    print("   🚀 Đang tải file lên máy chủ CapCut...")
                    up_info = upload_audio_to_capcut(f_path)
                    
                    print("   ⏳ Đang chờ AI bóc băng...")
                    json_res = capcut_stt(up_info["vid"], up_info["md5"], up_info["duration_ms"], lang)
                    
                    if json_res:
                        trang_thai = json_capcut_to_srt(json_res, srt_path)
                        
                        if trang_thai == "SUCCESS":
                            print(f"   ✅ Hoàn tất xuất phụ đề gốc: {os.path.basename(srt_path)}")
                            so_thanh_cong += 1
                        elif trang_thai == "NO_SPEECH":
                            print("   ⚠️ Video chỉ có nhạc nền / Không có lời thoại. Bỏ qua tạo SRT.")
                            so_khong_loi += 1
                        else: 
                            print("   ❌ Lỗi khi định dạng file SRT.")
                    else: 
                        print("   ❌ Máy chủ phản hồi quá lâu hoặc lỗi kết nối.")
                except Exception as e:
                    print(f"   ❌ Lỗi khi xử lý {os.path.basename(f_path)}: {e}")

            print(f"\n🎉 HOÀN THÀNH LÔ TRÍCH XUẤT:")
            print(f"   • Thành công xuất SRT gốc: {so_thanh_cong} file")
            print(f"   • Bỏ qua (đã có sẵn):      {so_bo_qua} file")
            print(f"   • Không có lời thoại:      {so_khong_loi} file")
            input("\nNhấn Enter để quay lại Menu...")
            
        elif chon == '0': 
            sys.exit(0)

if __name__ == "__main__":
    main_menu()