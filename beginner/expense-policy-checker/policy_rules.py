"""The company policy as DATA: an ordered list of rules, first match wins.

To change policy, edit thresholds in config.py or add/reorder rules here.
"""
from dataclasses import dataclass
from typing import Callable

import config
from state import APPROVED, REJECTED, MANAGER, NEED_INFO, ExpenseState


@dataclass(frozen=True)
class Rule:
    id: str
    description: str
    applies: Callable[[ExpenseState], bool]
    decision: str
    message: str            # may use {bill_limit} {auto_limit} {amounts} {currency}


RULES = [
    # ---- safety checks before the three policy rules -------------------------------------
    Rule("R0-MULTI-AMOUNT", "More than one different amount in the message",
         lambda e: "multiple_amounts" in e.flags, MANAGER,
         "Sent to manager: more than one amount found ({amounts}), please confirm the total"),
    Rule("R0-NO-AMOUNT", "No amount found",
         lambda e: e.amount is None, NEED_INFO,
         "Need more info: please share the expense amount (for example Rs 1200)"),
    Rule("R0-CURRENCY", "Amount is not in rupees",
         lambda e: e.currency != "INR", MANAGER,
         "Sent to manager: expense is in {currency} but policy limits are in Rs"),
    Rule("R0-DUPLICATE", "Looks like a repeat of an earlier approved/pending claim",
         lambda e: "possible_duplicate" in e.flags, MANAGER,
         "Sent to manager: looks like a duplicate of an earlier claim"),
    Rule("R0-BILL-UNKNOWN", "Above the bill limit and nothing says whether a bill exists",
         lambda e: config.ASK_WHEN_BILL_UNKNOWN and e.amount > config.BILL_REQUIRED_ABOVE and e.bill == "Unknown",
         NEED_INFO,
         "Need more info: bill is mandatory above Rs {bill_limit}, please attach it or confirm you have none"),
    # ---- the three rules from the task ----------------------------------------------------
    Rule("R1", "Amount above the bill limit AND no bill",
         lambda e: e.amount > config.BILL_REQUIRED_ABOVE and e.bill == "No", REJECTED,
         "Rejected as per policy: Bill mandatory above Rs {bill_limit}"),
    Rule("R2", "Amount below the auto-approve limit",
         lambda e: e.amount < config.AUTO_APPROVE_BELOW, APPROVED,
         "Approved as per policy: expenses under Rs {auto_limit} are auto-approved"),
    Rule("R3", "Everything else goes to the manager",
         lambda e: True, MANAGER,
         "Sent to your manager for approval as per policy"),
]
