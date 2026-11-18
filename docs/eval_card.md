# Báo cáo đánh giá — LogiX-VN

Tôi đánh giá agent hoàn tiền bằng cùng tập claim và seed để so sánh baseline với các bản gài lỗi. Mục tiêu là kiểm tra gate có chặn được hồi quy mà vẫn cho bản đúng đi qua hay không. Các bảng dưới được tổng hợp từ report trong src/reports/.

## Phiên bản và khả năng tái lập

Eval set v1 SHA `01cba42c4124`; v2 SHA `3f1765d27d44`.
Seeds chính: 11/22/33/44/55. Seed A/A: 66/77/88/99/110. MockLLM và judge replay; không cần API key.
Code/grader commit: xem commit chứa report; spec v1/v2 được commit cùng dữ liệu. Lệnh tái lập: `python -m lab9.submission` từ src.

## Kết quả đo

| Report/run ID | pass_rate | refund đúng | reply/ledger | pass_hat_5 | Gate |
|---|---:|---:|---:|---:|---|
| baseline_v1: E-swarm-20261118-01cb | 0.9857 | 0.9857 | 1.0 | — | merge |
| fixed_v1: E-fixed-20261118-01cb | 1.0 | 1.0 | 1.0 | — | merge |
| seeded_regression_v1: E-seeded_regression-20261118-01cb | 0.7143 | 0.8571 | 0.7857 | — | BLOCK: reply_ledger_consistent, refund_amount_correct, pass_rate |
| baseline_v2: E-swarm-20261118-3f17 | 0.9786 | 0.9786 | 1.0 | 0.8929 | merge |
| fixed_v2: E-fixed-20261118-3f17 | 1.0 | 1.0 | 1.0 | 1.0 | merge |
| honest_refactor_v2: E-honest_refactor-20261118-3f17 | 1.0 | 1.0 | 1.0 | 1.0 | merge |
| seeded_regression_v2: E-seeded_regression-20261118-3f17 | 0.6429 | 0.7857 | 0.7143 | 0.6429 | BLOCK: reply_ledger_consistent, pass_hat_5, refund_amount_correct, pass_rate, slice:money_movement/pass_rate, slice:adversarial/pass_rate, slice:denial/pass_rate |
| slice_regression_v2: E-slice_regression-20261118-3f17 | 0.9357 | 0.9357 | 1.0 | 0.8929 | BLOCK: slice:money_movement/pass_rate |
| flaky_regression_v2: E-flaky_regression-20261118-3f17 | 0.9143 | 0.9643 | 1.0 | 0.5714 | BLOCK: pass_hat_5, pass_rate, slice:money_movement/pass_rate |

Baseline chưa hoàn hảo: pass_rate v1 đạt 0.9857 và proposal_amount_correct còn cảnh báo. Metric đề xuất là chỉ số theo dõi, không chặn merge. Trên v2, slice_regression vẫn có pass_rate 0.9357 nhưng bị slice money_movement chặn; nếu chỉ nhìn điểm trung bình toàn bộ thì lỗi này sẽ lọt. Bản fixed và honest_refactor đều được gate chấp nhận.

## Paired bootstrap v1

Tôi tính Δ = PR − baseline. Mỗi mẫu bootstrap là một item sau khi lấy trung bình 5 seed, thay vì coi các seed là những ca độc lập. Cấu hình dùng 1000 lần lấy mẫu, RNG 2027 và CI 95% theo phương pháp percentile.

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

Tôi đặt sàn pass_hat_5 ở 0.8. Baseline v2 đạt 0.8929; hai bộ seed A/A cho cùng kết quả, nên sàn thấp hơn mức baseline đo được 0.0929. Trên lần chạy này, delta A/A của cả chất lượng và chi phí đều bằng 0. Khoảng cách đó giúp baseline không bị chặn, đồng thời vẫn giữ yêu cầu sàn tối thiểu 0.8 của bài. Hai bộ seed chưa đủ để ước lượng phân bố nhiễu của LLM thật; khi đổi model, cần chạy nhiều A/A trước khi chọn ngưỡng.

money_movement: pass_rate ≥0.95; adversarial ≥0.85; denial ≥0.90. Mỗi slice cũng chặn khi CI của Δ nằm hoàn toàn dưới 0. money_movement nhắm lỗi cộng điều khoản trên các ca có hoàn tiền; pass_hat_5 nhắm lỗi chỉ xuất hiện một seed. FM-08 dùng reply_ledger_consistent ≥1.0, không phụ thuộc dấu model_override.

Integrity kiểm tra coverage và multiplicity item/seed, tag slice, evaluator failure, missing/nonfinite metric và aggregate. Ratchet so với --base-spec chặn nới ngưỡng, bỏ metric/slice/blocking hoặc bỏ CI check.

## Giới hạn và vận hành

Kết quả hiện chỉ áp dụng cho 14 item v1 và 28 item v2 chạy bằng MockLLM. Cỡ mẫu nhỏ làm CI rộng; bộ judge replay cũng đã công khai nên chưa thể xem là held-out mới. Với lỗi kích hoạt ở khoảng 1/3 seed, chỉ 5 seed chưa bảo đảm phát hiện ổn định. Tôi giữ giới hạn này trong báo cáo, không hạ ngưỡng để cố bắt mọi lần.
Legacy swarm không ghi reply: metric FM-08 chỉ xác nhận không có phát biểu tiền quan sát được mâu thuẫn; không chứng minh tính đầy đủ của câu trả lời. Parser tiền hỗ trợ VND nguyên có ký hiệu tiền, cần mở rộng/test nếu có nhiều loại tiền hoặc câu chứa nhiều khoản khác nhau.
Baseline phải lấy từ commit được tin cậy. Integrity không có chữ ký mật mã; không chứng minh được tính xác thực của cả baseline lẫn mọi dòng bị làm giả nhất quán.
Eval owner: Lê Khánh Cường. Gate đỏ: không merge, điều tra trace và sửa grader/spec có version hoặc agent ở bài tiếp theo. Pilot chỉ sandbox public claims; chưa bật hoàn tiền production. Đổi item/label/seeds: tăng eval-set version và chạy baseline mới; đổi metric/spec: tăng metric_spec_version, giữ ratchet trên cùng eval set.

## Bằng chứng CLI

### Detection
```text
detection 100.00%; false alarms 0.00%
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
