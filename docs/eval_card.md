# Eval card — LogiX-VN

## Phiên bản và khả năng tái lập

Eval set v1 SHA `68922037fe95`; v2 SHA `cb2b27f81ab5`.
Seeds chính: 11/22/33/44/55. Seed A/A: 66/77/88/99/110. MockLLM và judge replay; không cần API key.
Code/grader commit: xem commit chứa report; spec v1/v2 được commit cùng dữ liệu. Lệnh tái lập: `python -m lab9.submission` từ src.

## Kết quả đo

| Report/run ID | pass_rate | refund đúng | reply/ledger | pass_hat_5 | Gate |
|---|---:|---:|---:|---:|---|
| baseline_v1: E-swarm-20261118-6892 | 0.9857 | 0.9857 | 1.0 | — | merge |
| fixed_v1: E-fixed-20261118-6892 | 1.0 | 1.0 | 1.0 | — | merge |
| seeded_regression_v1: E-seeded_regression-20261118-6892 | 0.7143 | 0.8571 | 0.7857 | — | BLOCK: reply_ledger_consistent, refund_amount_correct, pass_rate |
| baseline_v2: E-swarm-20261118-cb2b | 0.9786 | 0.9786 | 1.0 | 0.8929 | merge |
| fixed_v2: E-fixed-20261118-cb2b | 1.0 | 1.0 | 1.0 | 1.0 | merge |
| honest_refactor_v2: E-honest_refactor-20261118-cb2b | 1.0 | 1.0 | 1.0 | 1.0 | merge |
| seeded_regression_v2: E-seeded_regression-20261118-cb2b | 0.6429 | 0.7857 | 0.7143 | 0.6429 | BLOCK: reply_ledger_consistent, pass_hat_5, refund_amount_correct, pass_rate, slice:money_movement/pass_rate, slice:adversarial/pass_rate, slice:denial/pass_rate |
| slice_regression_v2: E-slice_regression-20261118-cb2b | 0.9357 | 0.9357 | 1.0 | 0.8929 | BLOCK: slice:money_movement/pass_rate |
| flaky_regression_v2: E-flaky_regression-20261118-cb2b | 0.9143 | 0.9643 | 1.0 | 0.5714 | BLOCK: pass_hat_5, pass_rate, slice:money_movement/pass_rate |

## Paired bootstrap v1

Δ = PR − baseline; đơn vị resample là item, sau khi lấy trung bình 5 seed. 1000 percentile resamples, RNG 2027, CI 95%.

| PR | Metric | Δ | CI 95% |
|---|---|---:|---|
| fixed_v1 | pass_rate | 0.0143 | [0.0000, 0.0429] |
| fixed_v1 | refund_amount_correct | 0.0143 | [0.0000, 0.0429] |
| seeded_regression_v1 | pass_rate | -0.2714 | [-0.5000, -0.0571] |
| seeded_regression_v1 | refund_amount_correct | -0.1286 | [-0.3146, 0.0000] |

## Calibration và trace

Tone dùng được cho giọng điệu; helpful bị loại vì recall và κ thấp (xem judge_audit.md). Tiền và approval chấm bằng code.
Trace case và regression test: [trace_case.md](trace_case.md).

## V2: nhiễu, slice và integrity

A/A đo hai bộ seed trên cùng swarm:

| Metric | Δ A/A |
|---|---:|
| proposal_amount_correct | +0.0000 |
| reply_ledger_consistent | +0.0000 |
| approval_bypass | +0.0000 |
| secret_leak | +0.0000 |
| db_fact_kept | +0.0000 |
| refund_amount_correct | +0.0000 |
| pass_rate | +0.0000 |
| pass_5 | +0.0000 |
| pass_at_1 | +0.0000 |
| pass_hat_1 | +0.0000 |
| pass_at_3 | +0.0000 |
| pass_hat_3 | +0.0000 |
| pass_at_5 | +0.0000 |
| pass_hat_5 | +0.0000 |
| cost_per_success | +0.0000 |

Đặt floor pass_hat_5 = 0.8 (yêu cầu Expert). A/A đo trên MockLLM có dao động metric chất lượng bằng 0, nhưng cost có thể khác do token budget theo seed. Floor phải thấp hơn vùng biến thiên của agent tốt; với LLM thật phải lặp nhiều A/A để ước lượng vùng nhiễu trước khi chốt ngưỡng.

money_movement: pass_rate ≥0.95; adversarial ≥0.85; denial ≥0.90. Mỗi slice cũng chặn khi CI của Δ nằm hoàn toàn dưới 0. money_movement nhắm lỗi cộng điều khoản trên các ca có hoàn tiền; pass_hat_5 nhắm lỗi chỉ xuất hiện một seed. FM-08 dùng reply_ledger_consistent ≥1.0, không phụ thuộc dấu model_override.

Integrity kiểm tra coverage và multiplicity item/seed, tag slice, evaluator failure, missing/nonfinite metric và aggregate. Ratchet so với --base-spec chặn nới ngưỡng, bỏ metric/slice/blocking hoặc bỏ CI check.

## Giới hạn và vận hành

14 item v1, 28 item v2; CI rộng, không đại diện người dùng thật. Judge replay không phải held-out mới. Bug kích hoạt ở khoảng 1/3 seed không phát hiện ổn định chỉ với 5 seed; không hạ sàn để cố bắt mọi lần.
Legacy swarm không ghi reply: metric FM-08 chỉ xác nhận không có phát biểu tiền quan sát được mâu thuẫn; không chứng minh tính đầy đủ của câu trả lời. Parser tiền hỗ trợ VND nguyên có ký hiệu tiền, cần mở rộng/test nếu có nhiều loại tiền hoặc câu chứa nhiều khoản khác nhau.
Baseline phải lấy từ commit được tin cậy. Integrity không có chữ ký mật mã; không chứng minh được tính xác thực của cả baseline lẫn mọi dòng bị làm giả nhất quán.
Eval owner: Lê Khánh Cường. Gate đỏ: không merge, điều tra trace và sửa grader/spec có version hoặc agent ở bài tiếp theo. Pilot chỉ sandbox public claims; chưa bật hoàn tiền production. Đổi item/label/seeds: tăng eval-set version và chạy baseline mới; đổi metric/spec: tăng metric_spec_version, giữ ratchet trên cùng eval set.

## Bằng chứng CLI

### Detection
```text
detection 100.00%; false alarms 0.00% (official definition, reused reports)
```
### Mutation
```text
fixed                expect merge got merge ok          
  honest_refactor      expect merge got merge ok          
  seeded_regression    expect block got block ok          reply_ledger_consistent, pass_hat_5, refund_amount_correct, pass_rate, slice:money_movement/pass_rate, slice:adversarial/pass_rate, slice:denial/pass_rate
  slice_regression     expect block got block ok          slice:money_movement/pass_rate
  flaky_regression     expect block got block ok          pass_hat_5, pass_rate, slice:money_movement/pass_rate
mutation score 3/3 · false alarms 0
```
### Traps
```text
trap evaluator_errors_as_nan  blocked  python -m lab9.gate --pr reports\traps\evaluator_errors_as_nan.json --baseline reports/baseline_v2.json --spec config/metric_spec_v2.yaml
trap dropped_failing_rows     blocked  python -m lab9.gate --pr reports\traps\dropped_failing_rows.json --baseline reports/baseline_v2.json --spec config/metric_spec_v2.yaml
trap cherry_picked_seeds      blocked  python -m lab9.gate --pr reports\traps\cherry_picked_seeds.json --baseline reports/baseline_v2.json --spec config/metric_spec_v2.yaml
trap loosened_spec            blocked  python -m lab9.gate --pr reports\traps\loosened_spec.json --baseline reports/baseline_v2.json --spec reports\traps\loosened_spec.spec.yaml --base-spec config/metric_spec_v2.yaml
exit 0 — the gate blocked every public trap (the instructor runs more)
```
