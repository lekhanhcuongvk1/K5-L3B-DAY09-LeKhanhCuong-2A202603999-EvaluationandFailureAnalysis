# Trace case: C-002@11

Run lỗi: `E-seeded_regression-20261118-01cb`. Đối chứng: cùng claim/seed trên `fixed`.

Ledger lỗi ghi 20000 VND, nhãn yêu cầu 0; status resolved thay vì denied.

Bước sai đầu tiên: **event 3, model_override**, payload `{"delay_days": 5}`.
Event 1 handoff giữ đúng claim và quyền tool. Event 2 investigator lấy dữ kiện DB; việc ghi đè delay_days bằng ticket ở event 3 mới tạo sai lệch. Quote phía sau sử dụng dữ kiện đã bị đổi; reply chỉ là hậu quả.

Failure mode: **FM-03**. Đối chứng fixed không có model_override; quote bằng 0, trạng thái denied và ledger 0 VND.

Regression test chạy được: `tests/test_lab9_student_regressions.py::test_lab9_first_wrong_step_claim_002`.
Test xác nhận DbFactKept, RefundAmountCorrect và lab8_pass đều false trên seeded_regression, true trên fixed.

Bằng chứng máy đọc: `src/reports/trace_case_C002.json`. Baseline liên quan: `E-swarm-20261118-01cb`.
Giới hạn: trace chứng minh bước ghi đè và hậu quả trong MockLLM; không chứng minh suy nghĩ bên trong model thật.
