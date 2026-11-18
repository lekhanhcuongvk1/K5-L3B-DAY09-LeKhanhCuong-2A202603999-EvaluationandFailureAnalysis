"""Student regression cases: outcome, reply, and integrity must agree."""
import copy

import pytest
from pydantic_evals.evaluators import EvaluatorContext

from lab9 import gate, stats
from lab9.graders import DbFactKept, RefundAmountCorrect, ReplyLedgerConsistent, ProposalAmountCorrect
from lab9.trace_case import investigate

pytestmark = pytest.mark.student


def context(trial, label):
    return EvaluatorContext(name="regression", inputs={}, metadata=None, expected_output=label,
                            output=trial, duration=0, _span_tree=None, attributes={}, metrics={})


@pytest.mark.parametrize("shape,good", [("seeded_regression", False), ("fixed", True)])
def test_lab9_first_wrong_step_claim_002(shape, good):
    case = investigate(shape, "C-002", 11)
    ctx = context(case["trial"], case["label"])
    assert DbFactKept().evaluate(ctx).value is good
    assert RefundAmountCorrect().evaluate(ctx).value is good
    assert case["trial"]["lab8_pass"] is good


@pytest.mark.parametrize("shape,good", [("seeded_regression", False), ("fixed", True)])
def test_lab9_zero_ledger_does_not_hide_pre_deducted_proposal(shape, good):
    case = investigate(shape, "C-013", 11)
    ctx = context(case["trial"], case["label"])
    assert case["trial"]["snapshot"]["refund_vnd"] == 0
    assert RefundAmountCorrect().evaluate(ctx).value is True
    assert ProposalAmountCorrect().evaluate(ctx).value is good


@pytest.mark.parametrize("proposal,good", [(35000, True), (0, False), (None, False)])
def test_lab9_proposal_is_independent_of_zero_ledger(proposal, good):
    trial = {"snapshot": {"refund_vnd": 0}, "result": {"proposal_amount": proposal}}
    assert ProposalAmountCorrect().evaluate(context(trial, {"proposal_amount": 35000})).value is good


@pytest.mark.parametrize("text,amount,good", [
    ("Đã hoàn 35.000đ cho O-909.", 20000, False),
    ("Đã hoàn 20,000 VND.", 20000, True),
    ("Đã hoàn 20 000 đồng.", 20000, True),
    ("LogiX đã hoàn phí 20.000đ cho đơn O-909 ạ.", 20000, True),
    ("Đã hoàn 20.000đ.", 0, False),
])
def test_lab9_reply_ledger_independent_of_proposal(text, amount, good):
    trial = {"snapshot": {"refund_vnd": amount}, "result": {"proposal_amount": 35000},
             "events": [{"kind": "reply", "payload": {"text": text}}]}
    assert ReplyLedgerConsistent().evaluate(context(trial, {})).value is good


def clean_report():
    rows = [{"item_id": "E-1", "seed": s, "pass_rate": True, "slices": ["money_movement"]} for s in (11, 22)]
    return {"manifest": {"items": 1, "seeds": [11, 22]}, "rows": rows,
            "metrics": {"pass_rate": 1.0}, "evaluator_failures": []}


@pytest.mark.parametrize("attack", ["duplicate", "crash", "tags", "forged_mean", "infinity"])
def test_lab9_advanced_integrity_on_green_runs(attack):
    base = clean_report()
    pr = copy.deepcopy(base)
    if attack == "duplicate":
        pr["rows"][1] = copy.deepcopy(pr["rows"][0])
    elif attack == "crash":
        pr["evaluator_failures"] = ["grader crashed even though summary is green"]
    elif attack == "tags":
        for row in pr["rows"]:
            row["slices"] = []
    elif attack == "forged_mean":
        pr["rows"][0]["pass_rate"] = False
    else:
        pr["rows"][0]["pass_rate"] = float("inf")
    spec = {"metrics": [{"id": "pass_rate", "blocking": True, "threshold": {"min": .8}}]}
    assert gate.integrity_check(base, base, spec) == []
    assert gate.integrity_check(pr, base, spec)


@pytest.mark.parametrize("args", [(0, 0, 1), (5, -1, 1), (5, 6, 1), (5, 2, 6), (5, 2, 0), (5.0, 2, 1), (True, 1, 1)])
def test_lab9_advanced_pass_k_rejects_invalid_counts(args):
    with pytest.raises(ValueError):
        stats.pass_at_k(*args)
    with pytest.raises(ValueError):
        stats.pass_hat_k(*args)
