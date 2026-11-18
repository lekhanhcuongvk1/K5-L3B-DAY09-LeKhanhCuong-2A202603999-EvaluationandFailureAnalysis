"""CI gate: compare a PR eval report with the main-branch baseline using the metric spec.

    python -m lab9.gate --pr reports/eval_workflow.json --baseline reports/baseline_v1.json

exit 0 = merge, exit 1 = blocked. Safety metrics: max 0, no averaging away.
Capability metrics: meet the floor AND the paired CI of (PR - main) is not entirely below 0.
Thresholds may only get stricter on the same eval-set version (ratchet).
"""

from __future__ import annotations

import argparse
import json
import math
from collections import Counter
from pathlib import Path

from lab8.console import utf8_stdio
from lab9 import stats
from lab9.eval import SPEC, load_spec, per_item


def integrity_check(pr: dict, base: dict, spec: dict, base_spec: dict | None = None) -> list[str]:
    """M7 (Expert): refuse to compare reports that cannot be trusted. Return a list of problems
    (empty = trustworthy). A gate that passes a broken report is worse than no gate.
    Must catch at least:
      - any metric value in pr["metrics"] that is NaN or inf
      - len(pr["rows"]) != manifest items x len(manifest seeds)   (dropped / duplicated rows)
      - the (item_id, seed) set of PR differs from the baseline's (cherry-picked seeds/items)
      - pr["evaluator_failures"] non-empty, or a row whose value for a graded spec metric is
        None (a crashed grader silently scores as "missing" and drops out of the mean)
      - base_spec given and a threshold in spec is LOOSER than in base_spec for the same
        eval-set version (ratchet: max may not rise, min may not fall, a blocking metric may
        not become non-blocking, a metric may not disappear; the same for spec["slices"],
        including dropping no_significant_drop)
      - an item's slice tags in PR rows differ from the baseline's (relabelling an item out of a
        slice hides its regression from the slice gate)"""
    problems = []
    graded = {m["id"] for m in spec["metrics"] if m.get("grader") == "code"}
    # Include registered graders, while keeping synthetic public-test specs usable.
    from lab9.graders import GRADERS
    graded |= {m["id"] for m in spec["metrics"] if m["id"] in GRADERS}
    for name, report in (("PR", pr), ("baseline", base)):
        manifest, rows = report.get("manifest", {}), report.get("rows", [])
        seeds = manifest.get("seeds", [])
        if not seeds or len(set(seeds)) != len(seeds):
            problems.append(f"{name}: invalid seed manifest")
        pairs = [(r.get("item_id"), r.get("seed")) for r in rows]
        items = {p[0] for p in pairs}
        if len(rows) != manifest.get("items", 0) * len(seeds) or len(items) != manifest.get("items"):
            problems.append(f"{name}: incomplete manifest coverage")
        if len(set(pairs)) != len(pairs) or set(pairs) != {(i, s) for i in items for s in seeds}:
            problems.append(f"{name}: duplicated or missing item/seed pairs")
        if report.get("evaluator_failures"):
            problems.append(f"{name}: evaluator failures")
        for mid, value in report.get("metrics", {}).items():
            if value is not None and (not isinstance(value, (int, float)) or not math.isfinite(value)):
                problems.append(f"{name}: nonfinite metric {mid}")
        for m in spec["metrics"]:
            value = report.get("metrics", {}).get(m["id"])
            if m.get("blocking") and (value is None or not isinstance(value, (int, float)) or not math.isfinite(value)):
                problems.append(f"{name}: invalid blocking metric {m['id']}")
        for row in rows:
            for mid in graded:
                value = row.get(mid)
                if value is None or not isinstance(value, (bool, int, float)) or not math.isfinite(value) or value not in (0, 1):
                    problems.append(f"{name}: invalid row metric {mid}")
            if "cost" in row and (not isinstance(row["cost"], (int, float)) or not math.isfinite(row["cost"]) or row["cost"] < 0):
                problems.append(f"{name}: invalid cost")
        # Recompute graded aggregates; reject a forged green summary over failing rows.
        for mid in graded:
            values = [r.get(mid) for r in rows]
            if values and all(isinstance(v, (bool, int, float)) and math.isfinite(v) for v in values):
                expected = sum(values) if mid in ("approval_bypass", "secret_leak") else round(sum(values) / len(values), 4)
                value = report.get("metrics", {}).get(mid)
                if value is None or not isinstance(value, (int, float)) or not math.isclose(value, expected, abs_tol=0.000051):
                    problems.append(f"{name}: aggregate mismatch {mid}")
        if rows and all(type(r.get("pass_rate")) is bool for r in rows):
            by_item = {}
            for row in rows:
                by_item.setdefault(row["item_id"], []).append(row["pass_rate"])
            for mid, value in report.get("metrics", {}).items():
                if mid.startswith(("pass_at_", "pass_hat_")):
                    try:
                        k = int(mid.rsplit("_", 1)[1])
                        fn = stats.pass_at_k if mid.startswith("pass_at_") else stats.pass_hat_k
                        expected = round(sum(fn(len(v), sum(v), k) for v in by_item.values()) / len(by_item), 4)
                        if value is None or not math.isclose(value, expected, abs_tol=0.000051):
                            problems.append(f"{name}: aggregate mismatch {mid}")
                    except (ValueError, TypeError):
                        problems.append(f"{name}: invalid reliability metric {mid}")
    def tags(report):
        return {(r.get("item_id"), r.get("seed")): sorted(r.get("slices") or []) for r in report.get("rows", [])}
    if Counter((r.get("item_id"), r.get("seed")) for r in pr.get("rows", [])) != Counter(
            (r.get("item_id"), r.get("seed")) for r in base.get("rows", [])):
        problems.append("PR item/seed coverage differs from baseline")
    if tags(pr) != tags(base):
        problems.append("PR slice tags differ from baseline")
    for report in (pr, base):
        seen = {}
        for row in report.get("rows", []):
            key, value = row.get("item_id"), sorted(row.get("slices") or [])
            if key in seen and seen[key] != value:
                problems.append("inconsistent slice tags across seeds")
            seen[key] = value
    if base_spec and spec.get("eval_set_version") == base_spec.get("eval_set_version"):
        for section in ("metrics", "slices"):
            key = (lambda m: m["id"]) if section == "metrics" else (lambda m: (m["name"], m["metric"]))
            current = {key(m): m for m in spec.get(section, [])}
            for old in base_spec.get(section, []):
                identity = key(old)
                new = current.get(identity)
                if new is None:
                    problems.append(f"ratchet: removed {identity}")
                    continue
                if old.get("blocking") and not new.get("blocking"):
                    problems.append(f"ratchet: disabled {identity}")
                before = old.get("threshold", {}) if section == "metrics" else old
                after = new.get("threshold", {}) if section == "metrics" else new
                for floor, value in before.items():
                    if floor in ("min", "max", "max_increase"):
                        changed = after.get(floor)
                        if changed is None or not isinstance(changed, (int, float)) or not math.isfinite(changed) or (
                                changed < value if floor == "min" else changed > value):
                            problems.append(f"ratchet: loosened {identity}/{floor}")
                    elif floor == "no_significant_drop" and value and not after.get(floor):
                        problems.append(f"ratchet: removed CI check {identity}")
        for field in ("eval_set", "labels", "seeds"):
            if base_spec.get(field) != spec.get(field):
                problems.append(f"ratchet: changed {field} without eval-set version")
    return list(dict.fromkeys(problems))


def slice_check(pr: dict, base: dict, spec: dict) -> tuple[list[str], list[str]]:
    """M5 (Advanced): an average can hide a regression on a small, important slice.
    For each entry of spec["slices"] ({"name", "metric", "min"?, "no_significant_drop"?, "blocking"}):
      - value = mean of per_item(pr, metric, slice_name=name)
      - fail if below "min", or if no_significant_drop and the paired CI over the slice's items
        lies entirely below 0
    Return (blocked ids like "slice:money_movement/pass_rate", report lines)."""
    blocked, lines = [], []
    for entry in spec.get("slices", []):
        name, metric = entry["name"], entry["metric"]
        identity = f"slice:{name}/{metric}"
        a, b = per_item(pr, metric, name), per_item(base, metric, name)
        fail = not a or set(a) != set(b)
        value = sum(a.values()) / len(a) if a else None
        if value is not None and value < entry.get("min", float("-inf")):
            fail = True
        note = ""
        if a and set(a) == set(b) and entry.get("no_significant_drop"):
            keys = sorted(a)
            bs = spec.get("bootstrap", {})
            delta, lo, hi = stats.paired_bootstrap([a[k] for k in keys], [b[k] for k in keys],
                n_resamples=bs.get("n_resamples", 1000), rng=bs.get("rng", 2027), confidence=bs.get("confidence", .95))
            note = f"delta={delta:+.3f} CI=[{lo:+.3f},{hi:+.3f}]"
            fail |= hi < 0
        if fail and entry.get("blocking"):
            blocked.append(identity)
        lines.append(f"  {identity}: {value} {note} {'BLOCK' if fail and entry.get('blocking') else 'warn' if fail else 'ok'}")
    return blocked, lines


def check(pr: dict, base: dict, spec: dict, base_spec: dict | None = None) -> tuple[list[str], list[str]]:
    if pr["manifest"]["eval_set_sha"] != base["manifest"]["eval_set_sha"]:
        return ["eval_set_sha"], ["  EVAL SET differs from the baseline's: re-run the baseline on the same eval set"]
    problems = integrity_check(pr, base, spec, base_spec)
    if problems:
        return ["integrity"], [f"  INTEGRITY {p}" for p in problems]
    blocked, lines = [], []
    bs = spec.get("bootstrap", {})
    for m in spec["metrics"]:
        mid, th, val = m["id"], m.get("threshold", {}), pr["metrics"].get(m["id"])
        verdict, note = "ok", ""
        if val is None:
            verdict = "missing"
        elif "max" in th and val > th["max"]:
            verdict = "fail"
        elif "min" in th and val < th["min"]:
            verdict = "fail"
        elif "max_increase" in th and base["metrics"].get(mid):
            if val > base["metrics"][mid] * (1 + th["max_increase"]):
                verdict = "fail"
        if th.get("no_significant_drop") and val is not None:
            a, b = per_item(pr, mid), per_item(base, mid)
            keys = sorted(set(a) & set(b))
            d, lo, hi = stats.paired_bootstrap([a[k] for k in keys], [b[k] for k in keys],
                                               n_resamples=bs.get("n_resamples", 1000), rng=bs.get("rng", 2027))
            note = f"Δ {d:+.3f} CI [{lo:+.3f}, {hi:+.3f}]"
            if hi < 0:
                verdict = "fail"
        if verdict != "ok" and m.get("blocking"):
            blocked.append(mid)
        label = {"ok": "ok", "missing": "MISSING"}.get(verdict, "BLOCK" if m.get("blocking") else "warn")
        lines.append(f"  {mid:<22} {val!s:<8} {json.dumps(th):<40} {note:<28} {label}")
    if spec.get("slices"):
        sb, sl = slice_check(pr, base, spec)
        blocked += sb
        lines += sl
    return blocked, lines


def main(argv: list[str] | None = None) -> int:
    utf8_stdio()
    ap = argparse.ArgumentParser(prog="lab9.gate")
    ap.add_argument("--pr", required=True)
    ap.add_argument("--baseline", required=True)
    ap.add_argument("--spec", default=str(SPEC))
    ap.add_argument("--base-spec", help="metric spec on main, for the ratchet check (M7)")
    args = ap.parse_args(argv)
    pr = json.loads(Path(args.pr).read_text(encoding="utf-8"))
    base = json.loads(Path(args.baseline).read_text(encoding="utf-8"))
    base_spec = load_spec(Path(args.base_spec)) if args.base_spec else None
    blocked, lines = check(pr, base, load_spec(Path(args.spec)), base_spec)
    print(f"gate: PR {pr['run_id']} vs main {base['run_id']} · eval set {pr['manifest']['eval_set_sha']}")
    print("\n".join(lines))
    if blocked:
        print(f"exit 1 — blocked: {', '.join(blocked)}")
        return 1
    print("exit 0 — merge")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
