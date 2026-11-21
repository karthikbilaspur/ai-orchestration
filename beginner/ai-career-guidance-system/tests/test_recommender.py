import unittest
from career_guidance.models import LearnerProfile
from career_guidance.agents.career_recommender import CareerRecommendationAgent


class RecommenderTests(unittest.TestCase):
    def test_interest_ranks_first(self):
        profile = LearnerProfile("B.Tech", ["python"], ["data science"], 2, "balanced", "internship")
        results = CareerRecommendationAgent().recommend(profile)
        self.assertEqual(results[0].career, "Data Scientist")
        self.assertGreaterEqual(results[0].score, results[-1].score)

    def test_returns_requested_number(self):
        profile = LearnerProfile("BSc", [], ["ai"], 1, "theoretical", "research")
        self.assertEqual(len(CareerRecommendationAgent().recommend(profile, top_n=2)), 2)


if __name__ == "__main__":
    unittest.main()
