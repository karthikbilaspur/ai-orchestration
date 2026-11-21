import json
import logging
from pathlib import Path

from support_system.agents.classifier import ClassifierAgent
from support_system.agents.priority import PriorityAgent
from support_system.agents.resolver import ResolverAgent
from support_system.agents.escalation import EscalationAgent
from support_system.models import CustomerCase, SupportReport


def configure_logging(path="log.txt"):
    logging.basicConfig(
        filename=path,
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        force=True,
    )


class CustomerSupportWorkflow:
    """Runs the four agents in sequence and passes each result to the next."""

    def __init__(self, classifier=None, priority=None, resolver=None, escalation=None):
        self.classifier = classifier or ClassifierAgent()
        self.priority_agent = priority or PriorityAgent()
        self.resolver = resolver or ResolverAgent()
        self.escalation_agent = escalation or EscalationAgent()

    def run(self, case: CustomerCase) -> SupportReport:
        logging.info("New customer support case received")
        logging.info("Handoff: intake -> classifier")
        classification = self.classifier.classify(case.issue)
        logging.info("Handoff: classifier -> priority")
        priority = self.priority_agent.assess(case, classification)
        logging.info("Handoff: priority -> resolver")
        resolution = self.resolver.resolve(case, classification)
        logging.info("Handoff: resolver -> escalation")
        escalation = self.escalation_agent.decide(case, classification, priority, resolution)
        logging.info("Case workflow completed; escalation=%s", escalation.required)
        return SupportReport(case, classification, priority, resolution, escalation)

    @staticmethod
    def save_report(report: SupportReport, path="support_case_report.json"):
        Path(path).write_text(json.dumps(report.to_dict(), indent=2), encoding="utf-8")
        logging.info("Support report saved to %s", path)


def collect_case(input_fn=input, output_fn=print):
    output_fn("\\n=== Customer Support Intake ===")
    issue = input_fn("1. What is your issue? ").strip()
    started = input_fn("2. When did the issue start? ").strip()
    impact_options = {
        "cannot use product", "major features affected", "minor inconvenience", "no impact"
    }
    while True:
        impact = input_fn(
            "3. Product impact (cannot use product / major features affected / "
            "minor inconvenience / no impact): "
        ).strip().lower()
        if impact in impact_options:
            break
        output_fn("Please choose one of the listed impact options.")
    tried = input_fn("4. Have you already tried troubleshooting? (yes/no; describe if useful): ").strip()
    while True:
        human = input_fn("5. Would you like to speak to a human representative? (yes/no): ").strip().lower()
        if human in {"yes", "y", "no", "n"}:
            break
        output_fn("Please answer yes or no.")
    return CustomerCase(issue, started, impact, tried, human in {"yes", "y"})
