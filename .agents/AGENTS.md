# CapCut AI Studio Project Rules

This file documents the workspace rules and details the Harness configuration used to manage, maintain, and test the CapCut TTS & STT integration project.

---

## 🦾 Harness: CapCut AI Studio

**Mục tiêu**: Tự động hóa quá trình bảo trì các cơ chế ký payload bảo mật của CapCut, cập nhật kho lưu trữ giọng đọc và phát triển các giao diện người dùng (Web/Desktop).

**Kích hoạt**: 
- Khi nhận được bất kỳ yêu cầu nào liên quan đến cập nhật chữ ký API, cập nhật danh sách giọng đọc, sửa lỗi giao diện, hay chạy kịch bản kiểm thử, bắt buộc kích hoạt kỹ năng điều phối (Orchestrator): `capcut_studio_orchestrator`.
- Trình quản lý tác nhân (Orchestrator) sẽ tự động khởi chạy đội ngũ tác nhân AI chuyên biệt bao gồm: API Engineer, Voice Registry Manager, UX Developer, và QA Tester dưới chế độ phối hợp nhóm (**Agent Team**).

---

## 👥 Đội ngũ tác nhân (Agent Team)

Chi tiết vai trò của các tác nhân được lưu tại thư mục: [agents/](file:///c:/Users/Trong/Desktop/capcut-tts-api-main/.agents/agents/)
- **[capcut_api_engineer](file:///c:/Users/Trong/Desktop/capcut-tts-api-main/.agents/agents/capcut_api_engineer.md)**: Chuyên gia reverse engineering, cập nhật thuật toán ký RSA, AWS SigV4, các tham số header (`sign`, `x-ss-stub`), giả lập thiết bị (`device.json`).
- **[voice_registry_manager](file:///c:/Users/Trong/Desktop/capcut-tts-api-main/.agents/agents/voice_registry_manager.md)**: Chuyên gia quản lý và kiểm tra chất lượng file `Voice.json`, chịu trách nhiệm thêm giọng mới và phân loại.
- **[app_ux_developer](file:///c:/Users/Trong/Desktop/capcut-tts-api-main/.agents/agents/app_ux_developer.md)**: Quản lý giao diện Web Studio (`static/`), thiết kế CSS, JS, và ứng dụng Desktop (`app_gui.py`).
- **[system_qa_tester](file:///c:/Users/Trong/Desktop/capcut-tts-api-main/.agents/agents/system_qa_tester.md)**: Chạy kiểm thử tự động, kiểm tra các luồng API, ranh giới dữ liệu và phát hiện lỗi.

---

## 🛠️ Kỹ năng (Harness Skills)

Các kỹ năng được tích hợp phục vụ dự án:
- **[capcut_api_updater](file:///c:/Users/Trong/Desktop/capcut-tts-api-main/.agents/skills/capcut_api_updater/SKILL.md)**: Hướng dẫn kỹ thuật cập nhật các cấu trúc ký API.
- **[voice_registry_helper](file:///c:/Users/Trong/Desktop/capcut-tts-api-main/.agents/skills/voice_registry_helper/SKILL.md)**: Hướng dẫn thu thập, làm sạch và cập nhật giọng đọc.
- **[capcut_studio_orchestrator](file:///c:/Users/Trong/Desktop/capcut-tts-api-main/.agents/skills/capcut_studio_orchestrator/SKILL.md)**: Skill điều phối chính của đội ngũ tác nhân.

---

## 📖 Lịch sử thay đổi (Changelog)

| Ngày | Nội dung thay đổi | Đối tượng | Lý do |
| :--- | :--- | :--- | :--- |
| 2026-06-23 | Khởi tạo cấu hình Harness ban đầu | Toàn bộ | Thiết lập hệ thống quản lý tác nhân tự động cho dự án CapCut |
