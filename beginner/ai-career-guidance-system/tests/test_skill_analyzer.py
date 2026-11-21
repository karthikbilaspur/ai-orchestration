import unittest
from career_guidance.models import LearnerProfile
from career_guidance.agents.skill_analyzer import SkillAnalyzerAgent


class SkillAnalyzerTests(unittest.TestCase):
    def test_python_is_recognized_as_strength(self):
        profile = LearnerProfile("BSc", ["python"], ["ai"], 2, "balanced", "job")
        result = SkillAnalyzerAgent().analyze(profile)
        self.assertTrue(any("Python" in item for item in result.strengths))
        self.assertNotIn("Python", result.skill_gaps)

    def test_no_language_gets_beginner_note(self):
        profile = LearnerProfile("High school", [], ["software development"], 1, "theoretical", "research")
        result = SkillAnalyzerAgent().analyze(profile)
        self.assertTrue(any("No programming experience" in x for x in result.strengths))


if __name__ == "__main__":
    unittest.main()
