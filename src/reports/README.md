# Báo cáo Lab 09

Thư mục này lưu kết quả chạy dùng để đối chiếu với báo cáo trong `docs/`. Các số liệu được sinh bằng script, không chỉnh sửa trực tiếp trong JSON.

| File | Nội dung |
|---|---|
| `baseline_v1.json`, `eval_fixed.json`, `eval_seeded_regression.json` | Baseline và hai bản đối chiếu của phần Core. |
| `baseline_v2.json`, `eval_*_v2.json` | Kết quả trên eval set v2, gồm các bản kiểm tra slice và lỗi chập chờn. |
| `detection.json` | Tỷ lệ phát hiện lỗi, báo nhầm và danh sách ca bị bỏ sót nếu có. |
| `aa_alternate_v2.json`, `aa_delta.json`, `aa_cli.txt` | Kết quả bộ seed thứ hai, chênh lệch A/A và output lệnh chính thức. |
| `judge_calibration.json` | Thống kê tone/helpful so với nhãn người. |
| `taxonomy_evidence.json`, `trace_case_C002.json` | Bằng chứng trace cho taxonomy và ca phân tích chi tiết. |
| `traps/` | Bốn report/spec cố tình làm sai để kiểm tra integrity và ratchet; không dùng làm baseline. |
| `submission_evidence.txt` | Log tổng hợp gate, mutation và trap của lần chạy đầy đủ. |

Chạy toàn bộ từ `src/` bằng `python -m lab9.submission`. Khi chỉ cần cập nhật văn bản từ report đã có, dùng `python -m lab9.submission --refresh-docs`; lệnh này kiểm tra report và chạy A/A chính thức, không đánh giá lại toàn bộ variant.

Do `.gitignore` bỏ qua thư mục này, cần chạy `git add -f src/reports` từ gốc repo khi nộp. `benchmark.json` và `crash.json` thuộc bài Day 8, không phải báo cáo bắt buộc của Day 9.
