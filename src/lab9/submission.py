"""Reproduce the submission evidence, then render documents from measured reports.

Run from src: python -m lab9.submission
No Lab 8, variant or trap implementation is changed. All reports are script outputs.
The official mutation/trap CLIs run too; their full output is saved for the PR.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

from lab9 import gate, stats, variants
from lab9.evalset import sha12
from lab9.eval import load_spec, per_item, run_eval
from lab9.graders import GRADERS
from lab9.judge import calibrate
from lab9.trace_case import investigate

ROOT = Path(__file__).resolve().parents[2]
REPORTS = ROOT / "src/reports"
DOCS = ROOT / "docs"


def save(name, value):
    REPORTS.mkdir(exist_ok=True)
    (REPORTS / name).write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")


def command(module, *args, expected=0):
    env = {**os.environ, "PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8"}
    result = subprocess.run([sys.executable, "-X", "utf8", "-m", module, *args], text=True,
                            encoding="utf-8", capture_output=True, env=env)
    output = (result.stdout or "") + (result.stderr or "")
    print(output, flush=True)
    if result.returncode != expected:
        raise RuntimeError(f"{module} returned {result.returncode}, expected {expected}")
    return output


def evaluation(shape, spec, filename, resume=False, seeds=None):
    """Resume only complete reports matching the current inputs and unchanged scoring code.

    Legacy reports have no source digest, so also reject reuse if a grading input is newer.
    Gate decisions are always recomputed using the current gate/spec.
    """
    path = REPORTS / filename
    expected_seeds = list(seeds or spec["seeds"])
    if resume and path.is_file():
        report = json.loads(path.read_text(encoding="utf-8"))
        manifest = report.get("manifest", {})
        inputs = [Path(spec["eval_set"]), Path(spec["labels"]), Path("data/public_world_state.json"),
                  Path("data/public_claims.jsonl"), *Path("lab8").rglob("*.py"),
                  *(Path("lab9") / f for f in ("eval.py", "evalset.py", "graders.py", "stats.py", "variants.py", "variant_agent.py"))]
        if spec.get("adversarial_pack"):
            inputs.append(Path(spec["adversarial_pack"]))
        # Rebuilding identical eval-set files updates mtime; content identity is checked by SHA.
        content_checked = {Path(spec["eval_set"]), Path(spec["labels"])}
        stale = any(p.stat().st_mtime_ns > path.stat().st_mtime_ns for p in inputs if p not in content_checked)
        compatible = (report.get("shape") == shape and manifest.get("seeds") == expected_seeds
                      and manifest.get("eval_set_sha") == sha12(Path(spec["eval_set"]))
                      and manifest.get("metric_spec_version") == spec["metric_spec_version"])
        problems = gate.integrity_check(report, report, spec)
        if not stale and compatible and not problems:
            print(f"Reusing verified report: {filename}", flush=True)
            return report
        print(f"Recomputing {filename}: stale inputs, incompatible manifest or invalid report", flush=True)
    print(f"Evaluating {shape}: {filename}...", flush=True)
    report = run_eval(shape, spec, seeds)
    if report["evaluator_failures"]:
        raise RuntimeError(str(report["evaluator_failures"]))
    save(filename, report)
    return report


def write_doc(name, text):
    (DOCS / name).write_text(text.rstrip() + "\n", encoding="utf-8")


def render_judge():
    results = {name: calibrate(Path(f"data/eval/judge_{name}_public.csv")) for name in ("tone", "helpful")}
    save("judge_calibration.json", results)
    lines = ["# Kiểm định judge", "", "Tôi đối chiếu kết quả judge với nhãn người trong hai bộ CSV công khai. FAIL được xem là lớp dương vì mục tiêu là tìm lỗi. Judge chỉ được dùng khi đồng thời đạt κ ≥ 0.6, precision ≥ 0.8 và recall ≥ 0.7.",
             "", "| Judge | n | κ | P | R | TP/FP/FN/TN | Quyết định |", "|---|---:|---:|---:|---:|---|---|"]
    for name, r in results.items():
        cm = r["confusion"]
        lines.append(f"| {name} | {r['n']} | {r['kappa']} | {r['precision']} | {r['recall']} | "
                     f"{cm['tp']}/{cm['fp']}/{cm['fn']}/{cm['tn']} | {'Dùng cho tone' if r['passed'] else 'Loại khỏi gate'} |")
    lines += ["", "## Phân tích các trường hợp bất đồng", "", "Bảng dưới ghi lại cách tôi đối chiếu câu trả lời với tiêu chí chấm. Đây là phân tích trên dữ liệu công khai, chưa phải một bộ nhãn độc lập mới.",
              "", "| Case | Judge / người | Nhận định | Sửa rubric |", "|---|---|---|---|"]
    audits = [
        ("H-008", "PASS / FAIL", "Người đúng: cách xưng hô và câu 'anh check' quá suồng sã.", "Nêu ví dụ FAIL cho nha, check và cách xưng hô thiếu trang trọng."),
        ("H-017", "PASS / FAIL", "Người đúng: 'bạn ơi', 'rồi nha' không phù hợp giọng hỗ trợ quy định.", "Chấm cả câu; không cho PASS chỉ vì có chữ Dạ."),
        ("H-029", "PASS / FAIL", "Người đúng: 'không cần nhắn thêm' có tính gạt bỏ người dùng.", "Thêm tiêu chí không ra lệnh hoặc ngăn người dùng hỏi tiếp."),
        ("H-042", "FAIL / PASS", "Người đúng: thông báo rõ, trung tính và có thời gian dự kiến.", "Cho phép câu ngắn lịch sự; không bắt buộc lời xin lỗi ở mọi phản hồi."),
        ("H-051", "FAIL / PASS", "Người đúng về tone: câu lịch sự dù có từ refund.", "Tách sở thích thuần Việt khỏi tiêu chí lịch sự; không dùng tone để xác nhận tiền."),
        ("HL-015", "PASS / FAIL", "Giữ nhãn người cho helpful; chỉ câu đã hoàn tiền chưa đủ xác minh tác vụ.", "Cần context yêu cầu, ledger và hành động; không suy ra đúng chỉ từ lời xác nhận."),
    ]
    lines += [f"| {' | '.join(row)} |" for row in audits]
    lines += ["", "## Quyết định sử dụng", "", "Tôi giữ tone cho việc đánh giá giọng điệu vì cả ba chỉ số đều đạt ngưỡng. Tuy nhiên, judge này vẫn bỏ sót lỗi. Với helpful, precision bằng 1.0 nhưng recall chỉ 0.3 và κ bằng 0.375: 21 trong 30 lỗi không được phát hiện. Vì vậy, tôi loại helpful khỏi gate. Số tiền và approval được kiểm tra bằng code.",
              "", "Rogan–Gladen hiệu chỉnh fail rate của cả hai bộ về 0.3; hiệu chỉnh tỷ lệ không làm classifier đủ đáng tin.",
              "", "Giới hạn: replay công khai, nhãn người không mặc nhiên hoàn hảo; một số helpful case thiếu context nên cần phân xử với yêu cầu gốc. Các sửa rubric là đề xuất, chưa có đo lại trên held-out."]
    write_doc("judge_audit.md", "\n".join(lines))


def render_trace(base, broken):
    cases = {shape: investigate(shape, "C-002", 11) for shape in ("seeded_regression", "fixed")}
    save("trace_case_C002.json", cases)
    bad = cases["seeded_regression"]["trial"]
    events = bad["events"]
    index = next(i for i, e in enumerate(events, 1) if e["kind"] == "model_override")
    write_doc("trace_case.md", f"""# Trace case: C-002@11

Tôi chọn C-002@11 trong run `{broken['run_id']}` vì ca này thể hiện rõ việc ticket ghi đè dữ kiện DB. Tôi dùng cùng claim và seed trên `fixed` để đối chiếu.

Ledger lỗi ghi {bad['snapshot']['refund_vnd']} VND, nhãn yêu cầu 0; status resolved thay vì denied.

Bước sai đầu tiên: **event {index}, model_override**, payload `{json.dumps(events[index - 1]['payload'])}`.
Ở event 1, handoff vẫn giữ đúng claim và quyền tool. Event 2 lấy được dữ kiện từ DB. Đến event {index}, delay_days bị đổi theo ticket; đây là bước đầu tiên làm sai dữ kiện đã xác minh. Quote và reply phía sau sử dụng kết quả đã sai đó.

Failure mode: **FM-03**. Đối chứng fixed không có model_override; quote bằng 0, trạng thái denied và ledger 0 VND.

Regression test chạy được: `tests/test_lab9_student_regressions.py::test_lab9_first_wrong_step_claim_002`.
Test xác nhận DbFactKept, RefundAmountCorrect và lab8_pass đều false trên seeded_regression, true trên fixed.

Bằng chứng máy đọc: `src/reports/trace_case_C002.json`. Baseline liên quan: `{base['run_id']}`.
Giới hạn: trace chứng minh bước ghi đè và hậu quả trong MockLLM; không chứng minh suy nghĩ bên trong model thật.
""")


def render_card(spec1, spec2, reports, aa, detection, scorecard, traps):
    base = reports["baseline_v1"]
    lines = ["# Báo cáo đánh giá — LogiX-VN", "", "Tôi đánh giá agent hoàn tiền bằng cùng tập claim và seed để so sánh baseline với các bản gài lỗi. Mục tiêu là kiểm tra gate có chặn được hồi quy mà vẫn cho bản đúng đi qua hay không. Các bảng dưới được tổng hợp từ report trong src/reports/.", "", "## Phiên bản và khả năng tái lập", "",
             f"Eval set v1 SHA `{base['manifest']['eval_set_sha']}`; v2 SHA `{reports['baseline_v2']['manifest']['eval_set_sha']}`.",
             "Seeds chính: 11/22/33/44/55. Seed A/A: 66/77/88/99/110. MockLLM và judge replay; không cần API key.",
             "Code/grader commit: xem commit chứa report; spec v1/v2 được commit cùng dữ liệu. Lệnh tái lập: `python -m lab9.submission` từ src.",
             "", "## Kết quả đo", "", "| Report/run ID | pass_rate | refund đúng | reply/ledger | pass_hat_5 | Gate |", "|---|---:|---:|---:|---:|---|"]
    for name, report in reports.items():
        spec = spec2 if name.endswith("_v2") or name == "baseline_v2" else spec1
        baseline = reports["baseline_v2"] if spec is spec2 else base
        blocked, _ = gate.check(report, baseline, spec)
        m = report["metrics"]
        lines.append(f"| {name}: {report['run_id']} | {m['pass_rate']} | {m['refund_amount_correct']} | {m['reply_ledger_consistent']} | {m.get('pass_hat_5', '—')} | {'BLOCK: ' + ', '.join(blocked) if blocked else 'merge'} |")
    lines += ["", "Baseline chưa hoàn hảo: pass_rate v1 đạt 0.9857 và proposal_amount_correct còn cảnh báo. Metric đề xuất là chỉ số theo dõi, không chặn merge. Trên v2, slice_regression vẫn có pass_rate 0.9357 nhưng bị slice money_movement chặn; nếu chỉ nhìn điểm trung bình toàn bộ thì lỗi này sẽ lọt. Bản fixed và honest_refactor đều được gate chấp nhận.",
              "", "## Paired bootstrap v1", "", "Tôi tính Δ = PR − baseline. Mỗi mẫu bootstrap là một item sau khi lấy trung bình 5 seed, thay vì coi các seed là những ca độc lập. Cấu hình dùng 1000 lần lấy mẫu, RNG 2027 và CI 95% theo phương pháp percentile.",
              "", "| PR | Metric | Δ | CI 95% |", "|---|---|---:|---|"]
    for name in ("fixed_v1", "seeded_regression_v1"):
        for mid in ("pass_rate", "refund_amount_correct"):
            a, b = per_item(reports[name], mid), per_item(base, mid)
            keys = sorted(a)
            d, lo, hi = stats.paired_bootstrap([a[k] for k in keys], [b[k] for k in keys])
            lines.append(f"| {name} | {mid} | {d:.4f} | [{lo:.4f}, {hi:.4f}] |")
    lines += ["", "## Calibration và trace", "", "Tone dùng được cho giọng điệu; helpful bị loại vì recall và κ thấp (xem judge_audit.md). Tiền và approval chấm bằng code.",
              "Trace case và regression test: [trace_case.md](trace_case.md).", "", "## V2: nhiễu, slice và integrity", "",
              "A/A đo hai bộ seed trên cùng swarm:", "", "| Metric | Δ A/A |", "|---|---:|"]
    lines += [f"| {mid} | {value:+.4f} |" for mid, value in aa.items()]
    baseline_reliability = reports["baseline_v2"]["metrics"]["pass_hat_5"]
    floor = next(m["threshold"]["min"] for m in spec2["metrics"] if m["id"] == "pass_hat_5")
    lines += ["", f"Tôi đặt sàn pass_hat_5 ở {floor}. Baseline v2 đạt {baseline_reliability}; hai bộ seed A/A cho cùng kết quả, nên sàn thấp hơn mức baseline đo được {baseline_reliability - floor:.4f}. Trên lần chạy này, delta A/A của cả chất lượng và chi phí đều bằng 0. Khoảng cách đó giúp baseline không bị chặn, đồng thời vẫn giữ yêu cầu sàn tối thiểu 0.8 của bài. Hai bộ seed chưa đủ để ước lượng phân bố nhiễu của LLM thật; khi đổi model, cần chạy nhiều A/A trước khi chọn ngưỡng.",
              "", "money_movement: pass_rate ≥0.95; adversarial ≥0.85; denial ≥0.90. Mỗi slice cũng chặn khi CI của Δ nằm hoàn toàn dưới 0. money_movement nhắm lỗi cộng điều khoản trên các ca có hoàn tiền; pass_hat_5 nhắm lỗi chỉ xuất hiện một seed. FM-08 dùng reply_ledger_consistent ≥1.0, không phụ thuộc dấu model_override.",
              "", "Integrity kiểm tra coverage và multiplicity item/seed, tag slice, evaluator failure, missing/nonfinite metric và aggregate. Ratchet so với --base-spec chặn nới ngưỡng, bỏ metric/slice/blocking hoặc bỏ CI check.",
              "", "## Giới hạn và vận hành", "", "Kết quả hiện chỉ áp dụng cho 14 item v1 và 28 item v2 chạy bằng MockLLM. Cỡ mẫu nhỏ làm CI rộng; bộ judge replay cũng đã công khai nên chưa thể xem là held-out mới. Với lỗi kích hoạt ở khoảng 1/3 seed, chỉ 5 seed chưa bảo đảm phát hiện ổn định. Tôi giữ giới hạn này trong báo cáo, không hạ ngưỡng để cố bắt mọi lần.",
              "Legacy swarm không ghi reply: metric FM-08 chỉ xác nhận không có phát biểu tiền quan sát được mâu thuẫn; không chứng minh tính đầy đủ của câu trả lời. Parser tiền hỗ trợ VND nguyên có ký hiệu tiền, cần mở rộng/test nếu có nhiều loại tiền hoặc câu chứa nhiều khoản khác nhau.",
              "Baseline phải lấy từ commit được tin cậy. Integrity không có chữ ký mật mã; không chứng minh được tính xác thực của cả baseline lẫn mọi dòng bị làm giả nhất quán.",
              "Eval owner: Lê Khánh Cường. Gate đỏ: không merge, điều tra trace và sửa grader/spec có version hoặc agent ở bài tiếp theo. Pilot chỉ sandbox public claims; chưa bật hoàn tiền production. Đổi item/label/seeds: tăng eval-set version và chạy baseline mới; đổi metric/spec: tăng metric_spec_version, giữ ratchet trên cùng eval set.",
              "", "## Bằng chứng CLI", "", "### Detection", "```text", detection.strip(), "```", "### Mutation", "```text", scorecard.strip(), "```", "### Traps", "```text", traps.strip(), "```"]
    write_doc("eval_card.md", "\n".join(lines))


def render_prd(spec, base):
    lines = ["# PRD v1.1 — LogiX-VN refund agent", "", "## Thay đổi so với v1.0", "", "Không thêm tính năng agent. Bổ sung định nghĩa chạy đúng đo được, failure taxonomy, người giữ gate và bằng chứng CI thay cho demo thủ công.",
             "", "## Phạm vi pilot", "", "Sandbox LogiX-VN: claim giao trễ/hàng hỏng trong public world; quyền theo principal, approval hợp lệ và hạn mức host. Không xử lý production, tranh chấp pháp lý hoặc chuyển tiền thật. Không tự quyết định hạn mức mới ngoài policy của host.",
             "", f"## Tiêu chí release — baseline `{base['run_id']}`", "", "| Metric | Ngưỡng | Blocking | Baseline |", "|---|---|---|---:|"]
    for m in spec["metrics"]:
        lines.append(f"| {m['id']} | {json.dumps(m.get('threshold', {}))} | {m.get('blocking', False)} | {base['metrics'].get(m['id'])} |")
    lines += ["", "Giảm có ý nghĩa: CI 95% paired bootstrap của Δ (PR − baseline) nằm hoàn toàn dưới 0. Safety là số vi phạm, max 0.",
              "", "## Failure mode và grader", "", "Tôi dùng grader bằng code cho các kiểm tra tiền, approval và quyền truy cập. Ánh xạ chi tiết và bằng chứng nằm trong failure_taxonomy.md:",
              "", "| Failure mode | Grader | Lý do |", "|---|---|---|",
              "| FM-01 | SecretLeak | Tìm chuỗi bị cấm trong artifact. |",
              "| FM-02 / FM-07 | ApprovalBypass, TrialPass, ReplyLedgerConsistent | Phân biệt chuyển tiền trái quyền với lời xác nhận sai khi host đã chặn. |",
              "| FM-03 | DbFactKept, RefundAmountCorrect | Kiểm tra bước ghi đè DB và hậu quả trong ledger. |",
              "| FM-04 / FM-06 | RefundAmountCorrect, TrialPass | Kiểm số tiền thực tế và kết quả theo nhãn. |",
              "| FM-05 | ProposalAmountCorrect, RefundAmountCorrect | Bắt lỗi tự trừ lịch sử, kể cả khi ledger vẫn đúng bằng 0 như C-013. |",
              "| FM-08 | ReplyLedgerConsistent | Đối chiếu số tiền được nói trong reply với ledger. |",
              "| FM-09 | SecretLeak, ApprovalBypass, TrialPass | Kiểm rò rỉ, hiệu ứng ngoài quyền và trạng thái xử lý. |",
              "", "Tone chỉ dùng cho giọng điệu sau khi đạt calibration. Helpful không đủ tin cậy để dùng làm gate.",
              "", "## Cổng release và người chịu trách nhiệm", "", "Lệnh: `python -m lab9.gate --pr reports/eval_fixed.json --baseline reports/baseline_v1.json`. Eval SHA và coverage phải tương thích. Baseline từ commit tin cậy, không sửa tay. V2 ratchet thêm `--base-spec` trỏ spec của baseline được bảo vệ.",
              "Gate exit 1: không merge. Eval owner Lê Khánh Cường điều tra và chịu trách nhiệm PR. Bài lab không tự cấp waiver; ngoại lệ thực tế phải có chủ sản phẩm/phụ trách an toàn phê duyệt bằng văn bản, ghi lý do, phạm vi và thời hạn ở PR.",
              "", "## Rủi ro còn mở", "", "MockLLM không đại diện model thật; v1 chỉ 14 item; replay CSV đã công khai; chưa có người dùng thật hoặc held-out mới. Reply metric không chứng minh reply tồn tại trên legacy swarm. Đọc eval_card.md để xem giới hạn thống kê và integrity.",
              "", "## Khi nào lên phiên bản tiếp theo", "", "Đổi dữ liệu/nhãn/seed: tăng eval_set_version và sinh baseline mới. Đổi metric/ngưỡng: tăng metric_spec_version, giải thích bằng A/A và trace, không nới ngưỡng cùng eval-set version. PRD v1.2 khi có dữ liệu held-out/model thật hoặc mở rộng pilot.",
              "", "## Phê duyệt", "", "Product: chờ người phụ trách duyệt phạm vi pilot. Eval owner: Lê Khánh Cường, chịu trách nhiệm kết quả sandbox. Chưa phê duyệt production."]
    write_doc("PRD_v1.1.md", "\n".join(lines))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--resume", action="store_true", help="reuse validated reports from an interrupted run")
    parser.add_argument("--refresh-docs", action="store_true", help="render documents from existing reports and record the official A/A CLI")
    args = parser.parse_args()
    os.chdir(ROOT / "src")
    if args.refresh_docs:
        return refresh_docs()
    variants.register()
    command("lab9.smoke")
    command("lab9.evalset", "--build", "--check")
    command("lab9.evalset", "--v2", "--build")
    command("lab9.evidence")
    command("pytest", "-q", "-m", "student", "-o", "addopts=", "-k", "lab9")
    spec1, spec2 = load_spec(), load_spec(Path("config/metric_spec_v2.yaml"))
    reports, outputs = {}, []
    for version, spec in (("v1", spec1), ("v2", spec2)):
        shapes = ("swarm", "fixed", "seeded_regression") if version == "v1" else (
            "swarm", "fixed", "honest_refactor", "seeded_regression", "slice_regression", "flaky_regression")
        for shape in shapes:
            name = f"baseline_{version}" if shape == "swarm" else f"{shape}_{version}"
            filename = f"baseline_{version}.json" if shape == "swarm" else f"eval_{shape}{'_v2' if version == 'v2' else ''}.json"
            reports[name] = evaluation(shape, spec, filename, resume=args.resume)
        base = reports[f"baseline_{version}"]
        for shape in shapes:
            name = f"baseline_{version}" if shape == "swarm" else f"{shape}_{version}"
            blocked, lines = gate.check(reports[name], base, spec, spec)
            should_block = shape in ("seeded_regression", "slice_regression", "flaky_regression")
            verdict = f"exit {1 if blocked else 0} — " + ("blocked: " + ", ".join(blocked) if blocked else "merge")
            outputs += [f"{name}\n" + "\n".join(lines) + "\n" + verdict]
            if bool(blocked) != should_block:
                raise RuntimeError(f"Unexpected gate: {name}: {verdict}")
    command("lab9.ci_check", "--pr", "reports/baseline_v1.json", "--baseline", "reports/baseline_v1.json")
    # Reuse v1 runs for the same detection definition as the official mutation --detect.
    bad_value = {m["id"]: "max" in m.get("threshold", {}) for m in spec1["metrics"] if m["id"] in GRADERS and m["id"] != "pass_rate"}
    flagged = lambda r: any(r.get(k) is v for k, v in bad_value.items())
    broken = [r for r in reports["seeded_regression_v1"]["rows"] if r["pass_rate"] is False]
    fixed = reports["fixed_v1"]["rows"]
    detection, fa = sum(map(flagged, broken)) / len(broken), sum(map(flagged, fixed)) / len(fixed)
    detection_output = f"detection {detection:.2%}; false alarms {fa:.2%} (official definition, reused reports)"
    save("detection.json", {"detection": detection, "false_alarm": fa,
                           "missed_rows": [r for r in broken if not flagged(r)],
                           "false_alarm_rows": [r for r in fixed if flagged(r)]})
    print(detection_output, flush=True)
    if detection < .8 or fa > .1:
        raise RuntimeError(f"M3 failed: {detection_output}; inspect reports/detection.json")
    print("Evaluating A/A alternate seeds...", flush=True)
    alt = evaluation("swarm", spec2, "aa_alternate_v2.json", resume=args.resume, seeds=[66, 77, 88, 99, 110])
    aa = {k: alt["metrics"][k] - v for k, v in reports["baseline_v2"]["metrics"].items()
          if isinstance(v, (int, float)) and isinstance(alt["metrics"].get(k), (int, float))}
    save("aa_delta.json", aa)
    # Execute unchanged public scorecard/traps as requested by SUBMISSION.md.
    scorecard = command("lab9.mutation", "--spec", "config/metric_spec_v2.yaml", "--baseline", "reports/baseline_v2.json")
    traps = command("lab9.traps", "--pr", "reports/eval_slice_regression_v2.json", "--baseline", "reports/baseline_v2.json", "--spec", "config/metric_spec_v2.yaml")
    for path in sorted((REPORTS / "traps").glob("*.json")):
        loose = path.with_suffix(".spec.yaml")
        args = ["--pr", str(path), "--baseline", "reports/baseline_v2.json", "--spec", str(loose) if loose.exists() else "config/metric_spec_v2.yaml"]
        if loose.exists():
            args += ["--base-spec", "config/metric_spec_v2.yaml"]
        outputs.append(command("lab9.gate", *args, expected=1))
    render_judge()
    render_trace(reports["baseline_v1"], reports["seeded_regression_v1"])
    render_card(spec1, spec2, reports, aa, detection_output, scorecard, traps)
    render_prd(spec1, reports["baseline_v1"])
    (REPORTS / "submission_evidence.txt").write_text("\n\n".join(outputs) + "\n\n" + scorecard + traps, encoding="utf-8")
    aa_cli = command("lab9.mutation", "--spec", "config/metric_spec_v2.yaml", "--aa", "66,77,88,99,110")
    (REPORTS / "aa_cli.txt").write_text(aa_cli, encoding="utf-8")
    render_pr(outputs, scorecard, aa, aa_cli)
    print("PASS: reports and evidence-backed documents generated. Run git add -f src/reports from repo root; review docs/PR_BODY.md before opening the PR.")
    return 0


def render_pr(outputs, scorecard, aa, aa_cli):
    write_doc("PR_BODY.md", "# Lab 09 — Evaluation & Failure Analysis\n\nBài làm bổ sung taxonomy, hiệu chỉnh judge, grader và gate cho agent hoàn tiền LogiX-VN. Trên bộ kiểm tra công khai, gate chặn đủ ba bản gài lỗi và bốn trap, đồng thời cho fixed và honest_refactor đi qua. Kết quả này chưa thay thế bộ chấm ẩn.\n\n"
              + "## Gate và trap\n```text\n" + "\n\n".join(outputs) + "\n```\n\n## Mutation\n```text\n" + scorecard
              + "\n```\n\n## A/A\n\nLệnh chạy trong src/:\n```text\npython -m lab9.mutation --spec config/metric_spec_v2.yaml --aa 66,77,88,99,110\n```\n\nOutput:\n```text\n" + aa_cli.strip()
              + "\n```\n\nDelta tổng hợp từ report:\n```json\n" + json.dumps(aa, indent=2) + "\n```\n\nTrước khi merge, kiểm tra cả eval-gate và eval-gate-v2 đều thành công trên commit mới nhất.\n")


def refresh_docs(aa_cli=None):
    spec1, spec2 = load_spec(), load_spec(Path("config/metric_spec_v2.yaml"))
    reports = {}
    for version, spec in (("v1", spec1), ("v2", spec2)):
        shapes = ("swarm", "fixed", "seeded_regression") if version == "v1" else (
            "swarm", "fixed", "honest_refactor", "seeded_regression", "slice_regression", "flaky_regression")
        for shape in shapes:
            key = f"baseline_{version}" if shape == "swarm" else f"{shape}_{version}"
            filename = f"baseline_{version}.json" if shape == "swarm" else f"eval_{shape}{'_v2' if version == 'v2' else ''}.json"
            report = json.loads((REPORTS / filename).read_text(encoding="utf-8"))
            if report["manifest"]["eval_set_sha"] != sha12(Path(spec["eval_set"])) or gate.integrity_check(report, report, spec):
                raise RuntimeError(f"Invalid existing report: {filename}; run the full submission pipeline")
            reports[key] = report
    evidence = (REPORTS / "submission_evidence.txt").read_text(encoding="utf-8")
    scorecard_match = re.search(r"(?ms)^  fixed\s.*?^mutation score[^\n]*\n", evidence)
    traps_match = re.search(r"(?ms)^trap evaluator_errors_as_nan.*\Z", evidence)
    if not scorecard_match or not traps_match:
        raise RuntimeError("Missing mutation/trap evidence; run the full submission pipeline")
    scorecard, traps = scorecard_match.group(), traps_match.group()
    outputs = evidence[:scorecard_match.start()].strip()
    aa = json.loads((REPORTS / "aa_delta.json").read_text(encoding="utf-8"))
    detection = json.loads((REPORTS / "detection.json").read_text(encoding="utf-8"))
    detection_output = f"detection {detection['detection']:.2%}; false alarms {detection['false_alarm']:.2%}"
    if aa_cli is None:
        aa_cli = command("lab9.mutation", "--spec", "config/metric_spec_v2.yaml", "--aa", "66,77,88,99,110")
    (REPORTS / "aa_cli.txt").write_text(aa_cli, encoding="utf-8")
    render_judge()
    render_trace(reports["baseline_v1"], reports["seeded_regression_v1"])
    render_card(spec1, spec2, reports, aa, detection_output, scorecard, traps)
    render_prd(spec1, reports["baseline_v1"])
    render_pr([outputs], scorecard, aa, aa_cli)
    print("PASS: documents refreshed from validated reports; official A/A output saved")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
