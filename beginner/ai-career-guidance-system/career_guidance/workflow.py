import json
import logging
from pathlib import Path

from career_guidance.agents.interviewer import InterviewerAgent
from career_guidance.agents.skill_analyzer import SkillAnalyzerAgent
from career_guidance.agents.career_recommender import CareerRecommendationAgent
from career_guidance.agents.roadmap import LearningRoadmapAgent
from career_guidance.models import GuidanceReport, LearnerProfile


def configure_logging(log_path: str = "log.txt") -> None:
    logging.basicConfig(
        filename=log_path,
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        force=True,
    )


class CareerGuidanceWorkflow:
    """Coordinates agent handoffs and assembles the final guidance report."""

    def __init__(self, interviewer=None, analyzer=None, recommender=None, roadmap=None):
        self.interviewer = interviewer or InterviewerAgent()
        self.analyzer = analyzer or SkillAnalyzerAgent()
        self.recommender = recommender or CareerRecommendationAgent()
        self.roadmap_agent = roadmap or LearningRoadmapAgent()

    def run(self, profile: LearnerProfile | None = None) -> GuidanceReport:
        logging.info("Workflow started")
        learner = profile or self.interviewer.collect()
        logging.info("Handoff 1: interviewer -> skill analyzer")
        analysis = self.analyzer.analyze(learner)
        logging.info("Handoff 2: skill analyzer -> career recommender")
        recommendations = self.recommender.recommend(learner)
        logging.info("Handoff 3: career recommender -> learning roadmap")
        roadmap = self.roadmap_agent.create(learner, recommendations[0])
        logging.info("Workflow completed")
        return GuidanceReport(learner, analysis, recommendations, roadmap)

    @staticmethod
    def save_report(report: GuidanceReport, path: str = "career_report.json") -> None:
        Path(path).write_text(json.dumps(report.to_dict(), indent=2), encoding="utf-8")
        logging.info("Report saved to %s", path)
