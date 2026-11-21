import unittest
from career_guidance.agents.interviewer import InterviewerAgent


class InterviewerTests(unittest.TestCase):
    def test_collects_profile(self):
        answers = iter([
            "B.Tech", "Python, Java", "AI, data science", "2",
            "hands-on projects", "internship"
        ])
        profile = InterviewerAgent(input_fn=lambda _: next(answers), output_fn=lambda _: None).collect()
        self.assertEqual(profile.education, "B.Tech")
        self.assertEqual(profile.languages, ["python", "java"])
        self.assertEqual(profile.interests, ["ai", "data science"])
        self.assertEqual(profile.daily_hours, 2.0)
        self.assertEqual(profile.target, "internship")


if __name__ == "__main__":
    unittest.main()
