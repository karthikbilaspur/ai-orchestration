from career_guidance.models import LearnerProfile, SkillAnalysis


class SkillAnalyzerAgent:
    """Derives a transparent starter skill profile from learner inputs."""

    TRACK_SKILLS = {
        "ai": ["Python", "linear algebra", "statistics", "machine learning", "model evaluation"],
        "software development": ["data structures", "algorithms", "Git", "APIs", "testing"],
        "data science": ["Python", "SQL", "statistics", "data visualization", "machine learning"],
        "cybersecurity": ["networking", "Linux", "security fundamentals", "scripting", "threat analysis"],
    }

    def analyze(self, profile: LearnerProfile) -> SkillAnalysis:
        languages = {x.lower() for x in profile.languages}
        strengths = [f"Programming exposure: {x}" for x in profile.languages]
        if "python" in languages:
            strengths.append("Python is a useful foundation across AI, data, and automation.")
        if "java" in languages or "c++" in languages:
            strengths.append("Experience with a compiled language supports core programming concepts.")
        if not profile.languages:
            strengths.append("No programming experience reported; a beginner-friendly path is appropriate.")

        relevant = []
        for interest in profile.interests:
            relevant.extend(self.TRACK_SKILLS[interest])
        gaps = []
        for skill in dict.fromkeys(relevant):
            if skill.lower() in languages:
                continue
            if skill.lower() == "python" and "python" in languages:
                continue
            gaps.append(skill)

        transferable = ["Problem decomposition", "Self-directed learning"]
        if profile.learning_preference == "hands-on projects":
            transferable.append("Project-oriented learning preference")
        summary = (
            f"Your profile shows {len(profile.languages)} listed programming language(s) "
            f"and interest in {', '.join(profile.interests)}. Build on existing knowledge "
            "and prioritize the missing foundations listed below."
        )
        return SkillAnalysis(strengths, gaps, transferable, summary)
