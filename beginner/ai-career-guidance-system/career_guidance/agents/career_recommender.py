from career_guidance.models import CareerMatch, LearnerProfile


class CareerRecommendationAgent:
    """Ranks career tracks using interests and beginner-friendly skill signals."""

    TRACKS = {
        "AI / Machine Learning Engineer": {
            "interest": "ai",
            "skills": ["Python", "linear algebra", "statistics", "machine learning", "model evaluation"],
        },
        "Software Developer": {
            "interest": "software development",
            "skills": ["data structures", "algorithms", "Git", "APIs", "testing"],
        },
        "Data Scientist": {
            "interest": "data science",
            "skills": ["Python", "SQL", "statistics", "data visualization", "machine learning"],
        },
        "Cybersecurity Analyst": {
            "interest": "cybersecurity",
            "skills": ["networking", "Linux", "security fundamentals", "scripting", "threat analysis"],
        },
    }

    def recommend(self, profile: LearnerProfile, top_n: int = 4) -> list[CareerMatch]:
        matches = []
        languages = {x.lower() for x in profile.languages}
        for career, data in self.TRACKS.items():
            interest = data["interest"]
            score = 35 if interest in profile.interests else 10
            rationale = []
            if interest in profile.interests:
                score += 45
                rationale.append(f"Matches your stated interest in {interest}.")
            else:
                rationale.append("Adjacent option; explore it if your interests change.")
            if "python" in languages and interest in {"ai", "data science"}:
                score += 10
                rationale.append("Your Python knowledge is a useful starting point.")
            if profile.daily_hours >= 2:
                score += 5
                rationale.append("Your available study time supports a steady practice routine.")
            elif profile.daily_hours < 1:
                rationale.append("Use a smaller, consistent study block to maintain progress.")
            if profile.target in {"internship", "job"}:
                rationale.append("Build a portfolio project and practice explaining your decisions.")
            matches.append(CareerMatch(
                career=career,
                score=min(score, 100),
                rationale=rationale,
                priority_skills=data["skills"],
            ))
        return sorted(matches, key=lambda x: x.score, reverse=True)[:top_n]
