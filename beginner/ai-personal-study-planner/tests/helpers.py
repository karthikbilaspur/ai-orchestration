from datetime import date

from study_planner.models import StudyRequirements

TODAY = date(2026, 11, 21)


def make_req(**kw):
    data = dict(subject="Python", level="beginner", deadline="2026-12-05", hours_daily=2,
                difficult_topics=["Error handling"], assessment="daily quizzes", start_date="2026-11-21")
    data.update(kw)
    return StudyRequirements(**data)
