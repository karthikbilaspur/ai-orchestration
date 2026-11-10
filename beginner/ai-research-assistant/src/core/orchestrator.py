"""Orchestrator: Sequential + Verification with Confidence-based Routing + Retry Loop."""
from .config import Config, DEFAULT_CONFIG
from .models import ResearchResult
from src.agents.planner import ResearchPlanner
from src.agents.researcher import ResearcherAgent
from src.agents.fact_checker import FactCheckerAgent
from src.agents.report_agent import ReportAgent
import os

class Orchestrator:
    def __init__(self, config: Config = DEFAULT_CONFIG, docs_dir="data/documents"):
        self.config = config
        self.planner = ResearchPlanner(max_subtopics=config.max_subtopics)
        self.researcher = ResearcherAgent(docs_dir=docs_dir)
        self.checker = FactCheckerAgent()
        self.reporter = ReportAgent()
        self.log = []

    def run(self, question: str) -> ResearchResult:
        self.log = [f"Question received: {question}"]
        subtopics = self.planner.plan(question)
        self.log.append(f"Planner → {len(subtopics)} subtopics: {', '.join(subtopics)}")
        retries = 0
        refined_queries = list(subtopics)
        while True:
            claims = self.researcher.research(question, refined_queries, self.config.max_claims_per_subtopic)
            self.log.append(f"Researcher → {len(claims)} claims retrieved (attempt {retries+1})")
            checked = self.checker.check_all(claims)
            confidence = self.checker.overall_confidence(checked)
            self.log.append(f"Fact Checker → confidence {confidence:.0%} (threshold {self.config.confidence_threshold:.0%})")
            if confidence >= self.config.confidence_threshold:
                self.log.append("Confidence Check → PASS → Report")
                status = "PASS"
                break
            if retries < self.config.max_retries:
                retries += 1
                self.log.append(f"Confidence Check → FAIL → Research Again (retry {retries}/{self.config.max_retries})")
                refined_queries = self.planner.refine(question, subtopics, checked)
                self.log.append(f"Refined queries: {', '.join(refined_queries)}")
                continue
            self.log.append("Confidence Check → FAIL, no retries left → Report with warning")
            status = "PASS_WITH_WARNING" if confidence >= 0.5 else "FAIL"
            break
        result = self.reporter.generate(question, subtopics, checked, confidence, status, retries, self.log)
        result.sources = sorted(set(c.source for c in checked if c.source))
        return result

def run_research(question, confidence_threshold=0.75, max_retries=2, docs_dir="data/documents"):
    cfg = Config(confidence_threshold=confidence_threshold, max_retries=max_retries)
    # Resolve docs dir relative to project root if needed
    if not os.path.exists(docs_dir):
        alt = os.path.join(os.path.dirname(__file__), "../../data/documents")
        if os.path.exists(alt):
            docs_dir = alt
    return Orchestrator(cfg, docs_dir=docs_dir).run(question)
