from career_guidance.models import CareerMatch, LearnerProfile


class LearningRoadmapAgent:
    """Builds a practical 30-day plan for the top-ranked career."""

    def create(self, profile: LearnerProfile, career: CareerMatch) -> list[dict]:
        skills = career.priority_skills
        preference = profile.learning_preference
        days = [
            ("Days 1-3", "Set up your environment and review fundamentals", skills[0]),
            ("Days 4-7", "Learn the core concepts and take structured notes", skills[1]),
            ("Days 8-12", "Practice guided exercises and solve small problems", skills[2]),
            ("Days 13-17", "Apply concepts to a small, realistic dataset or task", skills[3]),
            ("Days 18-22", "Build a focused portfolio mini-project", skills[4]),
            ("Days 23-26", "Test, debug, document, and improve the project", "Git and documentation"),
            ("Days 27-30", "Publish your work and prepare a short project walkthrough", "Portfolio and interview practice"),
        ]
        result = []
        for period, task, focus in days:
            if preference == "theoretical":
                activity = "Read a trusted resource, summarize concepts, and complete a short quiz."
            elif preference == "hands-on projects":
                activity = "Spend most of the session coding, experimenting, and recording what you learned."
            else:
                activity = "Split the session between concept study and practical exercises."
            result.append({
                "period": period,
                "focus": focus,
                "task": task,
                "activity": activity,
                "hours_per_day": profile.daily_hours,
            })
        return result
