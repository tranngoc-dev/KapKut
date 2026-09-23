---
name: capcut_api_updater
description: "Thực hiện các thay đổi, sửa đổi, cập nhật thuật toán ký mã bảo mật của CapCut hoặc các endpoint liên quan đến TTS và STT. Kích hoạt khi có yêu cầu cập nhật API chữ ký, x-ss-stub, x-khronos, sign, hoặc các tham số giả lập thiết bị (device.json)."
---

# Skill: CapCut API Updater

Tài liệu hướng dẫn bảo trì cấu trúc giao tiếp mạng với máy chủ CapCut.

## 1. Cơ chế ký bảo mật của CapCut (Signatures)

CapCut yêu cầu các header bảo mật cụ thể cho mọi request gửi lên `/lv/v1/common_task/new` và `/lv/v1/common_task/query`:

### a. `x-ss-stub`
- **Định nghĩa**: Là chuỗi MD5 của nội dung JSON body dạng rút gọn (compact JSON).
- **Cách tạo**: `hashlib.md5(body_text.encode("utf-8")).hexdigest()`.

### b. `sign`
- **Định nghĩa**: Chuỗi hash MD5 dựa trên một chuỗi salt kết hợp với đường dẫn URL, app version, device-time và tdid.
- **Cách tạo**: 
  `sign_str = f"9e2c|{path[-7:]}|3|{appvr}|{device_time}|{tdid}|11ac"`
  `sign = hashlib.md5(sign_str.encode("utf-8")).hexdigest()`

### c. Chữ ký RSA cho TTS Payload
- **Mô tả**: Gói tin SSML cần được ký bằng RSA PKCS#1 v1.5 bằng khóa Private/Public cụ thể được định nghĩa sẵn trong `TTS_SIGN_PUBLIC_KEY_PEM`.
- **Cách tạo**: Thực hiện ký RSA trực tiếp trên chuỗi `appid:{app_id}&did:{device_id}&creditDisable:false&ssml:{ssml_md5}`.

### d. AWS SigV4 cho STT VOD upload
- **Mô tả**: Để upload file lên không gian VOD của CapCut, cần sinh Header Authorization chuẩn AWS SigV4 bằng Python thuần (thông qua hàm `aws4_authorization`).

---

## 2. Quy trình xử lý khi API đổi cấu trúc

1. **Khảo sát gói tin**: Sử dụng Fiddler/Charles để xem cấu trúc request mới.
2. **Sử dụng chế độ Dry-Run**: Sử dụng tham số `--dry-run` để so sánh request do code tạo ra với request thực tế bắt được từ app:
   ```bash
   python capcut_common_task_client.py stt-new --audio-vid "test" --audio-md5 "test" --dry-run
   ```
3. **Cấu hình giả lập thiết bị**: Chỉnh sửa file `device.json` để đồng bộ các thông số `device_id`, `tdid`, `iid` với thiết bị thực tế đang chạy ổn định.
