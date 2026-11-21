"""Schedule Generator agent: deadline-aware, priority-weighted daily sessions."""
from __future__ import annotations

import logging
from datetime import date, timedelta

from study_planner.models import PRIORITY_WEIGHT

log = logging.getLogger(__name__)

PHASES = (
    "Learn the concepts and take notes.",
    "Work through examples and practice problems.",
    "Self-test from memory and write a short recap.",
)


def weighted_sequence(topics: list, n: int) -> list:
    """Smooth weighted round-robin: high-priority topics appear more often but stay spread out."""
    weights = [PRIORITY_WEIGHT[t["priority"]] for t in topics]
    total = sum(weights)
    current = [0] * len(topics)
    out = []
    for _ in range(n):
        for i, w in enumerate(weights):
            current[i] += w
        pick = max(range(len(topics)), key=lambda i: (current[i], -i))
        current[pick] -= total
        out.append(topics[pick])
    return out


class ScheduleGenerator:
    @staticmethod
    def revision_days(total_days: int) -> int:
        return 0 if total_days < 7 else min(3, max(1, total_days // 10))

    def generate(self, req, topics: list) -> list:
        """Return one session dict per calendar day from ``start_date`` to ``deadline``."""
        if not topics:
            raise ValueError("Cannot build a schedule without topics.")
        start = date.fromisoformat(req.start_date)
        total = req.days_available
        n_rev = self.revision_days(total)
        study_end = total - n_rev
        weekly = req.assessment == "weekly assessments"
        assess_days = set(range(6, study_end, 7)) if weekly else set()
        study_topics = weighted_sequence(topics, study_end - len(assess_days))
        rev_pool = [t["topic"] for t in topics if t["priority"] == "high"] or [t["topic"] for t in topics]

        sessions, seen, since_assessment, next_study = [], {}, [], 0
        for offset in range(total):
            day = (start + timedelta(days=offset)).isoformat()
            base = {"index": offset, "day": day, "hours": req.hours_daily, "priority": "high"}
            if offset >= study_end:
                k = offset - study_end
                covers = rev_pool[k::n_rev] or [rev_pool[k % len(rev_pool)]]
                sessions.append({**base, "topic": "Revision", "kind": "revision", "covers": covers,
                                 "activity": "Revise: " + ", ".join(covers) + ". Redo past mistakes and timed practice."})
            elif offset in assess_days:
                covers = list(dict.fromkeys(since_assessment)) or [topics[0]["topic"]]
                since_assessment = []
                sessions.append({**base, "topic": "Weekly assessment", "kind": "assessment", "covers": covers,
                                 "activity": "Take a timed assessment covering: " + ", ".join(covers) + "."})
            else:
                topic = study_topics[next_study]
                next_study += 1
                count = seen.get(topic["topic"], 0)
                seen[topic["topic"]] = count + 1
                since_assessment.append(topic["topic"])
                sessions.append({**base, "topic": topic["topic"], "priority": topic["priority"],
                                 "kind": "study", "covers": [topic["topic"]],
                                 "activity": PHASES[count % len(PHASES)]})
        log.info("Schedule: %d sessions (%d revision, %d assessment)", len(sessions), n_rev, len(assess_days))
        return sessions
