import unittest
from career_guidance.models import LearnerProfile, CareerMatch
from career_guidance.agents.roadmap import LearningRoadmapAgent


class RoadmapTests(unittest.TestCase):
    def test_creates_30_day_roadmap(self):
        profile = LearnerProfile("B.Tech", ["python"], ["ai"], 3, "hands-on projects", "job")
        match = CareerMatch("AI / ML Engineer", 95, [], ["Python", "math", "stats", "ML", "evaluation"])
        roadmap = LearningRoadmapAgent().create(profile, match)
        self.assertEqual(len(roadmap), 7)
        self.assertEqual(roadmap[0]["period"], "Days 1-3")
        self.assertEqual(roadmap[-1]["period"], "Days 27-30")
        self.assertIn("coding", roadmap[0]["activity"])


if __name__ == "__main__":
    unittest.main()
