"""Workflow: wires the agents together and owns persistence of plan and progress."""
from __future__ import annotations

import logging
from collections import Counter
from datetime import date, datetime
from pathlib import Path

from study_planner.agents.progress import ProgressEvaluator
from study_planner.agents.quiz import QuizGenerator
from study_planner.agents.schedule import ScheduleGenerator
from study_planner.agents.topic_breakdown import TopicBreakdownAgent
from study_planner.models import ValidationError
from study_planner.storage import StorageError, load_json, save_json

log = logging.getLogger(__name__)

PLAN_FILE = "study_plan.json"
PROGRESS_FILE = "progress.json"


class StudyPlannerWorkflow:
    def __init__(self, data_dir=".", today: date | None = None):
        self.data_dir = Path(data_dir)
        self.today = today
        self.topics = TopicBreakdownAgent()
        self.scheduler = ScheduleGenerator()
        self.quizzes = QuizGenerator()
        self.progress = ProgressEvaluator()

    @property
    def plan_path(self) -> Path:
        return self.data_dir / PLAN_FILE

    @property
    def progress_path(self) -> Path:
        return self.data_dir / PROGRESS_FILE

    def _today(self) -> date:
        return self.today or date.today()

    def run(self, requirements) -> dict:
        """Run collector output through topic breakdown -> schedule -> quizzes -> progress."""
        log.info("Handoff: collector -> topic breakdown")
        topics = self.topics.breakdown(requirements)
        log.info("Handoff: topic breakdown -> schedule generator")
        sessions = self.scheduler.generate(requirements, topics)
        log.info("Handoff: schedule generator -> quiz generator")
        questions = self.quizzes.generate(requirements, sessions)
        log.info("Handoff: quiz generator -> progress evaluator")
        progress = self.progress.evaluate(sessions, [], self._today())
        kinds = Counter(s["kind"] for s in sessions)
        report = {
            "generated_at": datetime.now().isoformat(timespec="seconds"),
            "requirements": requirements.to_dict(),
            "summary": {"total_days": len(sessions), "study_sessions": kinds["study"],
                        "assessment_sessions": kinds["assessment"], "revision_sessions": kinds["revision"],
                        "total_hours": progress["hours_total"]},
            "topic_priorities": topics,
            "daily_schedule": sessions,
            "practice_questions": questions,
            "progress": progress,
        }
        save_json(self.plan_path, report)
        self.progress.save(self.progress_path, progress)  # a new plan starts with fresh progress
        log.info("Plan saved to %s", self.plan_path)
        return report

    def load_plan(self) -> dict:
        plan = load_json(self.plan_path)
        if plan is None:
            raise StorageError(f"No study plan found at {self.plan_path}. Run the 'plan' command first.")
        return plan

    def _update(self, indices, add: bool) -> dict:
        plan = self.load_plan()
        sessions = plan["daily_schedule"]
        for i in indices:
            if not 0 <= i < len(sessions):
                raise ValidationError(f"Session {i} does not exist (plan has sessions 0-{len(sessions) - 1}).")
        completed = set(self.progress.load_completed(self.progress_path))
        completed = completed | set(indices) if add else completed - set(indices)
        result = self.progress.evaluate(sessions, completed, self._today())
        self.progress.save(self.progress_path, result)
        log.info("Sessions %s %s", sorted(indices), "completed" if add else "unmarked")
        return result

    def mark_done(self, indices) -> dict:
        return self._update(list(indices), add=True)

    def mark_undone(self, indices) -> dict:
        return self._update(list(indices), add=False)

    def status(self) -> dict:
        plan = self.load_plan()
        completed = self.progress.load_completed(self.progress_path)
        return self.progress.evaluate(plan["daily_schedule"], completed, self._today())

    def upcoming(self, days: int = 7) -> dict:
        """Return overdue sessions and those due within the next ``days`` days."""
        plan = self.load_plan()
        sessions = plan["daily_schedule"]
        done = set(self.progress.load_completed(self.progress_path))
        today = self._today().isoformat()
        limit = date.fromordinal(self._today().toordinal() + days).isoformat()
        pending = [s for s in sessions if s["index"] not in done]
        return {"overdue": [s for s in pending if s["day"] < today],
                "upcoming": [s for s in pending if today <= s["day"] < limit]}
