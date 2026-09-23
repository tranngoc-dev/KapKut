---
name: voice_registry_helper
description: "Cập nhật, làm sạch hoặc kiểm tra tính hợp lệ của danh sách các giọng đọc trong Voice.json. Kích hoạt khi có yêu cầu thêm giọng đọc mới, lọc giọng đọc, hoặc kiểm tra xem các giọng đọc trong Voice.json còn hoạt động hay không."
---

# Skill: Voice Registry Helper

Tài liệu hướng dẫn quản trị và cập nhật danh sách giọng đọc CapCut.

## 1. Định dạng file `Voice.json`

File `Voice.json` chứa một mảng JSON các đối tượng giọng đọc, mỗi đối tượng bắt buộc có các trường sau:

```json
  {
    "lan": "Mã ngôn ngữ rút gọn (vi, en, zh, ja, ko...)",
    "lang": "Mã ngôn ngữ đầy đủ (vi-VN, en-US, zh-CN, ja-JP, ko-KR...)",
    "voice_type": "Mã định danh giọng đọc nội bộ (ví dụ: BV074_streaming)",
    "display_name": "Tên hiển thị thân thiện (ví dụ: Cô Gái Hoạt Ngôn)",
    "resource_id": "Mã tài nguyên âm thanh (ví dụ: 7102355709945188865)",
    "captured_at": "Thời gian ghi nhận (định dạng ISO 8601)"
  }
```

---

## 2. Quy trình cập nhật Giọng đọc mới

1. **Thu thập dữ liệu**: Bắt gói tin API CapCut. Tìm kiếm các endpoint chứa danh sách effect/voice (ví dụ: `/media_api/v1/effect/list`).
2. **Lọc trùng lặp**: Trước khi ghi vào `Voice.json`, kiểm tra xem `voice_type` hoặc `resource_id` đã tồn tại chưa:
   - Nếu đã có, bỏ qua hoặc cập nhật `resource_id` nếu nó bị thay đổi.
3. **Phân loại giới tính**: Chạy hàm `guess_gender` (trong `server.py`) để kiểm tra nhãn giới tính sẽ hiển thị cho giọng đọc đó.
4. **Kiểm tra tính hoạt động (Health check)**:
   - Gửi một request TTS thử nghiệm sử dụng giọng đọc mới với câu chào ngắn để xem server CapCut có trả về HTTP 200 và liên kết âm thanh hay không.
