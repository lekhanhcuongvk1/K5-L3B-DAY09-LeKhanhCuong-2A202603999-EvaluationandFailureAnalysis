# Lab 09 — kế hoạch và cách tái lập

## Checkpoint

1. **M0:** chép src từ repo gốc Day 8, giữ nguyên lab8, cài requirements bằng Python 3.11–3.13. Smoke phải PASS.
2. **M1:** taxonomy có mã cố định, layer và bằng chứng; gắn failure_modes có thể tái build; labels riêng, provenance đầy đủ; kiểm v1/v2 không lỗi.
3. **M2:** confusion với FAIL dương, P/R, kappa và Rogan–Gladen; tone đạt floors, helpful không đạt; audit ít nhất năm bất đồng và đề xuất sửa rubric.
4. **M3:** ApprovalBypass, RefundAmountCorrect, metric reply_ledger_consistent blocking; trace C-002@11 với event sai đầu tiên và test fixed đối chứng. Detection >=80%, false alarm <=10%.
5. **M4:** paired percentile bootstrap theo item; baseline swarm; fixed qua, seeded_regression chặn trên pass_rate; section eval trong harness map 1.2.
6. **M5:** map adversarial mechanism sang FM, >=3 item/FM bị tấn công; slices money_movement và adversarial blocking cùng denial.
7. **M6:** pass@k/pass^k có validation, floor pass_hat_5 >=0.8; A/A hai bộ seed và giới hạn cỡ mẫu.
8. **M7:** kiểm report integrity và spec ratchet; baseline tự so vẫn qua; duplicate, missing, invalid values, evaluator failures và đổi slice bị chặn; public mutation 3/3, không báo nhầm.
9. **Submission:** tài liệu sinh từ report thật, force-add reports, PR nội bộ fork, CI xanh, merge main rồi nộp link fork lên LMS trước hạn.

## Kiểm tra ngắn đã chạy khi triển khai

- M0 smoke: PASS; pip check không xung đột.
- Eval set v1: 14 item, v2: 28 item; check 0 problem.
- Test có marker student của Lab 09 và regression bổ sung: 52 passed trong lần kiểm tra cuối.
- Tone κ=0.757, P=0.857, R=0.8; helpful κ=0.375, P=1.0, R=0.3.
- Trace C-002@11: event 3 model_override là bước sai đầu tiên trên seeded_regression; ledger 20.000 thay vì 0; fixed không ghi đè và ledger 0.

Các thông tin trên không thay thế kết quả toàn pipeline hoặc GitHub Actions. Bộ chấm ẩn và key anchor giảng viên không có trong repo.

## Tái lập kết quả

Từ src với .venv đang bật:

```powershell
python -m lab9.submission
```

Script dừng khi test, gate, detection, mutation hoặc trap không đạt. Các report được sinh bằng code; judge_audit, trace_case, eval_card, PRD_v1.1 và PR_BODY lấy số liệu từ kết quả đo. Khi có lỗi, cần kiểm tra log và sửa nguyên nhân trước khi chạy lại, không sửa tay report để đổi kết quả.

Sau khi script in PASS, từ gốc repo:

```powershell
git add src docs
git add -f src/reports
git commit
git push -u origin starter/d09
```

Dùng nội dung docs/PR_BODY.md làm mô tả PR starter/d09 → main **trong fork cá nhân**. Bật Actions nếu fork chưa bật. Chờ cả eval-gate và eval-gate-v2 xanh, kiểm tra baseline/report đã có trong PR, rồi merge. Giảng viên chấm main; bài chưa hoàn tất chỉ vì test local xanh. Nộp link repo fork lên LMS theo hạn của ca.

## Giới hạn thiết kế

- MockLLM/replay, dữ liệu nhỏ, không chứng minh khả năng chạy production.
- Legacy swarm không ghi reply; reply metric kiểm các phát biểu tiền quan sát được, không đo độ đầy đủ của câu trả lời.
- Integrity cần baseline/spec đáng tin cậy; ratchet dùng --base-spec của nhánh gốc được bảo vệ khi chạy trên thay đổi spec.
- Giữ nguyên lab8, variants, variant_agent, traps và test giảng viên. Evidence shape chỉ đăng ký tạm trong tiến trình, dùng công tắc công khai để quan sát lỗi.
