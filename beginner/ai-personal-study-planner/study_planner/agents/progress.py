"""Progress Evaluator agent: tracks completed sessions and reports schedule health."""
from __future__ import annotations

import logging
from datetime import date, timedelta

from study_planner.storage import load_json, save_json

log = logging.getLogger(__name__)


class ProgressEvaluator:
    def evaluate(self, sessions: list, completed_indices, today: date | None = None) -> dict:
        today = today or date.today()
        total = len(sessions)
        done = sorted({i for i in completed_indices if isinstance(i, int) and 0 <= i < total})
        done_set = set(done)
        percent = int(100 * len(done) / total + 0.5) if total else 0

        per_topic: dict = {}
        for i, s in enumerate(sessions):
            entry = per_topic.setdefault(s.get("topic", "Unknown"), {"completed": 0, "total": 0})
            entry["total"] += 1
            entry["completed"] += i in done_set

        today_s = today.isoformat()
        due = [i for i, s in enumerate(sessions) if s.get("day") and s["day"] <= today_s]
        overdue = [i for i in due if i not in done_set and sessions[i]["day"] < today_s]
        next_idx = next((i for i in range(total) if i not in done_set), None)

        if total and percent == 100:
            status = "complete"
        elif not due:
            status = "not started"
        else:
            behind = len([i for i in due if i not in done_set])
            status = "on track" if behind <= 0 else ("slightly behind" if behind <= 2 else "behind schedule")

        return {
            "completed_session_indices": done, "completed": len(done), "total": total,
            "completion_percent": percent,
            "hours_completed": round(sum(sessions[i].get("hours", 0) for i in done), 2),
            "hours_total": round(sum(s.get("hours", 0) for s in sessions), 2),
            "per_topic": per_topic, "overdue_sessions": overdue, "streak_days": self._streak(sessions, done_set, today),
            "next_session": next_idx, "status": status,
        }

    @staticmethod
    def _streak(sessions, done_set, today: date) -> int:
        by_day: dict = {}
        for i, s in enumerate(sessions):
            if s.get("day"):
                by_day.setdefault(s["day"], []).append(i in done_set)
        day = today
        if not all(by_day.get(day.isoformat(), [False])):
            day -= timedelta(days=1)  # today's work is not finished yet; count back from yesterday
        streak = 0
        while by_day.get(day.isoformat()) and all(by_day[day.isoformat()]):
            streak += 1
            day -= timedelta(days=1)
        return streak

    @staticmethod
    def save(path, data: dict) -> None:
        save_json(path, data)
        log.info("Progress saved: %s%% complete", data.get("completion_percent"))

    @staticmethod
    def load_completed(path) -> list:
        data = load_json(path, default={}) or {}
        return list(data.get("completed_session_indices", []))
