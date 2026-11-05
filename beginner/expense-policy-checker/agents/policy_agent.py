"""Agent 2: apply the policy rules in order. No LLM, so the same claim always gets the same answer."""
import config
from policy_rules import RULES
from state import ExpenseState, APPROVED, MANAGER, money


class PolicyAgent:
    def __init__(self):
        self._seen = set()          # claims already approved or pending, used for duplicate detection

    def run(self, s: ExpenseState) -> ExpenseState:
        key = None
        if s.sender and s.amount is not None:
            # first word of the place only, so "Truffles" and "Truffles Bangalore" count as the same venue
            key = (s.sender.lower(), s.amount, s.currency, (s.place or s.category).lower().split()[0])
            if key in self._seen:
                s.flags.append("possible_duplicate")

        context = {"bill_limit": config.BILL_REQUIRED_ABOVE, "auto_limit": config.AUTO_APPROVE_BELOW,
                   "amounts": ", ".join(f"Rs {money(a)}" for a in s.amounts_found), "currency": s.currency}
        for rule in RULES:
            if rule.applies(s):
                s.decision, s.rule_id, s.rule_description = rule.decision, rule.id, rule.description
                s.message = rule.message.format(**context)
                break

        # Rejected / need-info claims do not block a corrected resubmission.
        if key and s.decision in (APPROVED, MANAGER):
            self._seen.add(key)
        return s
