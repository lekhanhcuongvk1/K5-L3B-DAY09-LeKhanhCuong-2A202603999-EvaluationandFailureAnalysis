# Trace case: C-002@11

Tôi chọn C-002@11 trong run `E-seeded_regression-20261118-01cb` vì ca này thể hiện rõ việc ticket ghi đè dữ kiện DB. Tôi dùng cùng claim và seed trên `fixed` để đối chiếu.

Ledger lỗi ghi 20000 VND, nhãn yêu cầu 0; status resolved thay vì denied.

Bước sai đầu tiên: **event 3, model_override**, payload `{"delay_days": 5}`.
Ở event 1, handoff vẫn giữ đúng claim và quyền tool. Event 2 lấy được dữ kiện từ DB. Đến event 3, delay_days bị đổi theo ticket; đây là bước đầu tiên làm sai dữ kiện đã xác minh. Quote và reply phía sau sử dụng kết quả đã sai đó.

Failure mode: **FM-03**. Đối chứng fixed không có model_override; quote bằng 0, trạng thái denied và ledger 0 VND.

Regression test chạy được: `tests/test_lab9_student_regressions.py::test_lab9_first_wrong_step_claim_002`.
Test xác nhận DbFactKept, RefundAmountCorrect và lab8_pass đều false trên seeded_regression, true trên fixed.

Bằng chứng máy đọc: `src/reports/trace_case_C002.json`. Baseline liên quan: `E-swarm-20261118-01cb`.
Giới hạn: trace chứng minh bước ghi đè và hậu quả trong MockLLM; không chứng minh suy nghĩ bên trong model thật.
