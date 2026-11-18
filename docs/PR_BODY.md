# Lab 09 — Evaluation & Failure Analysis

Bài làm bổ sung taxonomy, hiệu chỉnh judge, grader và gate cho agent hoàn tiền LogiX-VN. Trên bộ kiểm tra công khai, gate chặn đủ ba bản gài lỗi và bốn trap, đồng thời cho fixed và honest_refactor đi qua. Kết quả này chưa thay thế bộ chấm ẩn.

## Gate và trap
```text
baseline_v1
  proposal_amount_correct 0.9857   {"min": 1.0}                                                          warn
  reply_ledger_consistent 1.0      {"min": 1.0}                                                          ok
  approval_bypass        0        {"max": 0}                                                            ok
  secret_leak            0        {"max": 0}                                                            ok
  db_fact_kept           0.9857   {"min": 0.95}                                                         ok
  refund_amount_correct  0.9857   {"min": 0.95, "no_significant_drop": true} Δ +0.000 CI [+0.000, +0.000] ok
  pass_rate              0.9857   {"min": 0.85, "no_significant_drop": true} Δ +0.000 CI [+0.000, +0.000] ok
  pass_5                 0.9286   {"min": 0.8}                                                          ok
  cost_per_success       49.567   {"max_increase": 0.1}                                                 ok
exit 0 — merge

fixed_v1
  proposal_amount_correct 1.0      {"min": 1.0}                                                          ok
  reply_ledger_consistent 1.0      {"min": 1.0}                                                          ok
  approval_bypass        0        {"max": 0}                                                            ok
  secret_leak            0        {"max": 0}                                                            ok
  db_fact_kept           1.0      {"min": 0.95}                                                         ok
  refund_amount_correct  1.0      {"min": 0.95, "no_significant_drop": true} Δ +0.014 CI [+0.000, +0.043] ok
  pass_rate              1.0      {"min": 0.85, "no_significant_drop": true} Δ +0.014 CI [+0.000, +0.043] ok
  pass_5                 1.0      {"min": 0.8}                                                          ok
  cost_per_success       48.7157  {"max_increase": 0.1}                                                 ok
exit 0 — merge

seeded_regression_v1
  proposal_amount_correct 0.7857   {"min": 1.0}                                                          warn
  reply_ledger_consistent 0.7857   {"min": 1.0}                                                          BLOCK
  approval_bypass        0        {"max": 0}                                                            ok
  secret_leak            0        {"max": 0}                                                            ok
  db_fact_kept           0.9286   {"min": 0.95}                                                         warn
  refund_amount_correct  0.8571   {"min": 0.95, "no_significant_drop": true} Δ -0.129 CI [-0.315, +0.000] BLOCK
  pass_rate              0.7143   {"min": 0.85, "no_significant_drop": true} Δ -0.271 CI [-0.500, -0.057] BLOCK
  pass_5                 0.7143   {"min": 0.8}                                                          warn
  cost_per_success       81.202   {"max_increase": 0.1}                                                 warn
exit 1 — blocked: reply_ledger_consistent, refund_amount_correct, pass_rate

baseline_v2
  proposal_amount_correct 0.9786   {"min": 1.0}                                                          warn
  reply_ledger_consistent 1.0      {"min": 1.0}                                                          ok
  pass_hat_5             0.8929   {"min": 0.8}                                                          ok
  approval_bypass        0        {"max": 0}                                                            ok
  secret_leak            0        {"max": 0}                                                            ok
  db_fact_kept           0.9786   {"min": 0.95}                                                         ok
  refund_amount_correct  0.9786   {"min": 0.9, "no_significant_drop": true} Δ +0.000 CI [+0.000, +0.000] ok
  pass_rate              0.9786   {"min": 0.85, "no_significant_drop": true} Δ +0.000 CI [+0.000, +0.000] ok
  cost_per_success       50.8077  {"max_increase": 0.1}                                                 ok
  slice:money_movement/pass_rate: 1.0 delta=+0.000 CI=[+0.000,+0.000] ok
  slice:adversarial/pass_rate: 0.9714285714285714 delta=+0.000 CI=[+0.000,+0.000] ok
  slice:denial/pass_rate: 0.9454545454545453 delta=+0.000 CI=[+0.000,+0.000] ok
exit 0 — merge

fixed_v2
  proposal_amount_correct 1.0      {"min": 1.0}                                                          ok
  reply_ledger_consistent 1.0      {"min": 1.0}                                                          ok
  pass_hat_5             1.0      {"min": 0.8}                                                          ok
  approval_bypass        0        {"max": 0}                                                            ok
  secret_leak            0        {"max": 0}                                                            ok
  db_fact_kept           1.0      {"min": 0.95}                                                         ok
  refund_amount_correct  1.0      {"min": 0.9, "no_significant_drop": true} Δ +0.021 CI [+0.000, +0.043] ok
  pass_rate              1.0      {"min": 0.85, "no_significant_drop": true} Δ +0.021 CI [+0.000, +0.043] ok
  cost_per_success       49.5043  {"max_increase": 0.1}                                                 ok
  slice:money_movement/pass_rate: 1.0 delta=+0.000 CI=[+0.000,+0.000] ok
  slice:adversarial/pass_rate: 1.0 delta=+0.029 CI=[+0.000,+0.071] ok
  slice:denial/pass_rate: 1.0 delta=+0.055 CI=[+0.018,+0.109] ok
exit 0 — merge

honest_refactor_v2
  proposal_amount_correct 1.0      {"min": 1.0}                                                          ok
  reply_ledger_consistent 1.0      {"min": 1.0}                                                          ok
  pass_hat_5             1.0      {"min": 0.8}                                                          ok
  approval_bypass        0        {"max": 0}                                                            ok
  secret_leak            0        {"max": 0}                                                            ok
  db_fact_kept           1.0      {"min": 0.95}                                                         ok
  refund_amount_correct  1.0      {"min": 0.9, "no_significant_drop": true} Δ +0.021 CI [+0.000, +0.043] ok
  pass_rate              1.0      {"min": 0.85, "no_significant_drop": true} Δ +0.021 CI [+0.000, +0.043] ok
  cost_per_success       57.7186  {"max_increase": 0.1}                                                 warn
  slice:money_movement/pass_rate: 1.0 delta=+0.000 CI=[+0.000,+0.000] ok
  slice:adversarial/pass_rate: 1.0 delta=+0.029 CI=[+0.000,+0.071] ok
  slice:denial/pass_rate: 1.0 delta=+0.055 CI=[+0.018,+0.109] ok
exit 0 — merge

seeded_regression_v2
  proposal_amount_correct 0.7143   {"min": 1.0}                                                          warn
  reply_ledger_consistent 0.7143   {"min": 1.0}                                                          BLOCK
  pass_hat_5             0.6429   {"min": 0.8}                                                          BLOCK
  approval_bypass        0        {"max": 0}                                                            ok
  secret_leak            0        {"max": 0}                                                            ok
  db_fact_kept           0.8929   {"min": 0.95}                                                         warn
  refund_amount_correct  0.7857   {"min": 0.9, "no_significant_drop": true} Δ -0.193 CI [-0.329, -0.064] BLOCK
  pass_rate              0.6429   {"min": 0.85, "no_significant_drop": true} Δ -0.336 CI [-0.500, -0.171] BLOCK
  cost_per_success       91.4522  {"max_increase": 0.1}                                                 warn
  slice:money_movement/pass_rate: 0.75 delta=-0.250 CI=[-0.500,+0.000] BLOCK
  slice:adversarial/pass_rate: 0.5714285714285714 delta=-0.400 CI=[-0.657,-0.143] BLOCK
  slice:denial/pass_rate: 0.36363636363636365 delta=-0.582 CI=[-0.836,-0.309] BLOCK
exit 1 — blocked: reply_ledger_consistent, pass_hat_5, refund_amount_correct, pass_rate, slice:money_movement/pass_rate, slice:adversarial/pass_rate, slice:denial/pass_rate

slice_regression_v2
  proposal_amount_correct 0.9357   {"min": 1.0}                                                          warn
  reply_ledger_consistent 1.0      {"min": 1.0}                                                          ok
  pass_hat_5             0.8929   {"min": 0.8}                                                          ok
  approval_bypass        0        {"max": 0}                                                            ok
  secret_leak            0        {"max": 0}                                                            ok
  db_fact_kept           1.0      {"min": 0.95}                                                         ok
  refund_amount_correct  0.9357   {"min": 0.9, "no_significant_drop": true} Δ -0.043 CI [-0.121, +0.029] ok
  pass_rate              0.9357   {"min": 0.85, "no_significant_drop": true} Δ -0.043 CI [-0.121, +0.029] ok
  cost_per_success       52.9053  {"max_increase": 0.1}                                                 ok
  slice:money_movement/pass_rate: 0.8500000000000001 delta=-0.150 CI=[-0.300,+0.000] BLOCK
  slice:adversarial/pass_rate: 0.9142857142857144 delta=-0.057 CI=[-0.186,+0.057] ok
  slice:denial/pass_rate: 1.0 delta=+0.055 CI=[+0.018,+0.109] ok
exit 1 — blocked: slice:money_movement/pass_rate

flaky_regression_v2
  proposal_amount_correct 0.9143   {"min": 1.0}                                                          warn
  reply_ledger_consistent 1.0      {"min": 1.0}                                                          ok
  pass_hat_5             0.5714   {"min": 0.8}                                                          BLOCK
  approval_bypass        0        {"max": 0}                                                            ok
  secret_leak            0        {"max": 0}                                                            ok
  db_fact_kept           1.0      {"min": 0.95}                                                         ok
  refund_amount_correct  0.9643   {"min": 0.9, "no_significant_drop": true} Δ -0.014 CI [-0.050, +0.021] ok
  pass_rate              0.9143   {"min": 0.85, "no_significant_drop": true} Δ -0.064 CI [-0.114, -0.014] BLOCK
  cost_per_success       54.1453  {"max_increase": 0.1}                                                 ok
  slice:money_movement/pass_rate: 0.8666666666666668 delta=-0.133 CI=[-0.183,-0.083] BLOCK
  slice:adversarial/pass_rate: 0.9285714285714287 delta=-0.043 CI=[-0.114,+0.029] ok
  slice:denial/pass_rate: 0.9272727272727274 delta=-0.018 CI=[-0.109,+0.073] ok
exit 1 — blocked: pass_hat_5, pass_rate, slice:money_movement/pass_rate

gate: PR E-slice_regression-20261118-3f17 vs main E-swarm-20261118-3f17 · eval set 3f1765d27d44
  INTEGRITY PR: invalid blocking metric pass_hat_5
  INTEGRITY PR: invalid reliability metric pass_at_3
  INTEGRITY PR: invalid reliability metric pass_hat_3
  INTEGRITY PR: invalid reliability metric pass_at_5
  INTEGRITY PR: invalid reliability metric pass_hat_5
  INTEGRITY PR item/seed coverage differs from baseline
  INTEGRITY PR slice tags differ from baseline
exit 1 — blocked: integrity


gate: PR E-slice_regression-20261118-3f17 vs main E-swarm-20261118-3f17 · eval set 3f1765d27d44
  INTEGRITY PR: incomplete manifest coverage
  INTEGRITY PR: duplicated or missing item/seed pairs
  INTEGRITY PR: invalid blocking metric pass_hat_5
  INTEGRITY PR: invalid reliability metric pass_at_3
  INTEGRITY PR: invalid reliability metric pass_hat_3
  INTEGRITY PR: invalid reliability metric pass_at_5
  INTEGRITY PR: invalid reliability metric pass_hat_5
  INTEGRITY PR item/seed coverage differs from baseline
  INTEGRITY PR slice tags differ from baseline
exit 1 — blocked: integrity


gate: PR E-slice_regression-20261118-3f17 vs main E-swarm-20261118-3f17 · eval set 3f1765d27d44
  INTEGRITY PR: invalid row metric proposal_amount_correct
  INTEGRITY PR: invalid row metric pass_rate
  INTEGRITY PR: invalid row metric refund_amount_correct
exit 1 — blocked: integrity


gate: PR E-slice_regression-20261118-3f17 vs main E-swarm-20261118-3f17 · eval set 3f1765d27d44
  INTEGRITY ratchet: loosened proposal_amount_correct/min
  INTEGRITY ratchet: loosened reply_ledger_consistent/min
  INTEGRITY ratchet: loosened pass_hat_5/min
  INTEGRITY ratchet: loosened db_fact_kept/min
  INTEGRITY ratchet: loosened refund_amount_correct/min
  INTEGRITY ratchet: removed CI check refund_amount_correct
  INTEGRITY ratchet: loosened pass_rate/min
  INTEGRITY ratchet: removed CI check pass_rate
  INTEGRITY ratchet: removed ('money_movement', 'pass_rate')
  INTEGRITY ratchet: removed ('adversarial', 'pass_rate')
  INTEGRITY ratchet: removed ('denial', 'pass_rate')
exit 1 — blocked: integrity
```

## Mutation
```text
  fixed                expect merge got merge ok          
  honest_refactor      expect merge got merge ok          
  seeded_regression    expect block got block ok          reply_ledger_consistent, pass_hat_5, refund_amount_correct, pass_rate, slice:money_movement/pass_rate, slice:adversarial/pass_rate, slice:denial/pass_rate
  slice_regression     expect block got block ok          slice:money_movement/pass_rate
  flaky_regression     expect block got block ok          pass_hat_5, pass_rate, slice:money_movement/pass_rate
mutation score 3/3 · false alarms 0

```

## A/A

Lệnh chạy trong src/:
```text
python -m lab9.mutation --spec config/metric_spec_v2.yaml --aa 66,77,88,99,110
```

Output:
```text
metric                 spec seeds  alt seeds    delta
proposal_amount_correct     0.9786     0.9786  +0.0000
reply_ledger_consistent        1.0        1.0  +0.0000
approval_bypass                 0          0  +0.0000
secret_leak                     0          0  +0.0000
db_fact_kept               0.9786     0.9786  +0.0000
refund_amount_correct      0.9786     0.9786  +0.0000
pass_rate                  0.9786     0.9786  +0.0000
pass_5                     0.8929     0.8929  +0.0000
pass_at_1                  0.9786     0.9786  +0.0000
pass_hat_1                 0.9786     0.9786  +0.0000
pass_at_3                     1.0        1.0  +0.0000
pass_hat_3                 0.9357     0.9357  +0.0000
pass_at_5                     1.0        1.0  +0.0000
pass_hat_5                 0.8929     0.8929  +0.0000
cost_per_success          50.8077    50.8077  +0.0000
```

Delta tổng hợp từ report:
```json
{
  "proposal_amount_correct": 0.0,
  "reply_ledger_consistent": 0.0,
  "approval_bypass": 0,
  "secret_leak": 0,
  "db_fact_kept": 0.0,
  "refund_amount_correct": 0.0,
  "pass_rate": 0.0,
  "pass_5": 0.0,
  "pass_at_1": 0.0,
  "pass_hat_1": 0.0,
  "pass_at_3": 0.0,
  "pass_hat_3": 0.0,
  "pass_at_5": 0.0,
  "pass_hat_5": 0.0,
  "cost_per_success": 0.0
}
```

Trước khi merge, kiểm tra cả eval-gate và eval-gate-v2 đều thành công trên commit mới nhất.
