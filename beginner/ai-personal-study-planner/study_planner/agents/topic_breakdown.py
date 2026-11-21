"""Topic Breakdown agent: builds a subject-aware topic outline with priorities."""
from __future__ import annotations

import logging
import re

log = logging.getLogger(__name__)

FOUNDATIONS = "Prerequisites and foundations"
ADVANCED = "Advanced theory and current methods"
REVISION = "Revision and exam practice"

BANKS = {
    "programming": ["Syntax and core constructs", "Data types and data structures",
                    "Functions and modular design", "Error handling and debugging",
                    "Libraries, tooling and testing", "Projects and practice problems", REVISION],
    "math": ["Definitions and notation", "Core theorems and rules", "Worked problems",
             "Proof and reasoning techniques", "Applications", "Timed problem sets", REVISION],
    "science": ["Core concepts and terminology", "Laws and fundamental principles",
                "Experiments and evidence", "Quantitative problem solving",
                "Real-world applications", REVISION],
    "language": ["Vocabulary and pronunciation", "Grammar essentials", "Reading comprehension",
                 "Listening and speaking practice", "Writing practice", REVISION],
    "generic": ["Core concepts and terminology", "Fundamental principles", "Worked examples",
                "Applied problem solving", REVISION],
}

KEYWORDS = {
    "programming": {"python", "java", "javascript", "typescript", "c", "c++", "c#", "rust", "go",
                    "sql", "programming", "coding", "algorithms", "software", "html", "css", "react"},
    "math": {"math", "maths", "mathematics", "algebra", "calculus", "statistics", "geometry",
             "probability", "trigonometry"},
    "science": {"physics", "chemistry", "biology", "science", "geology", "astronomy"},
    "language": {"english", "spanish", "french", "german", "hindi", "japanese", "kannada",
                 "tamil", "language", "grammar"},
}


class TopicBreakdownAgent:
    def detect_domain(self, subject: str) -> str:
        tokens = set(re.findall(r"[a-z0-9+#]+", subject.lower()))
        for domain, words in KEYWORDS.items():
            if tokens & words:
                return domain
        return "generic"

    @staticmethod
    def _matches(difficult: str, topic: str) -> bool:
        a, b = difficult.lower(), topic.lower()
        return a == b or (len(a) >= 3 and (a in b or b in a))

    def breakdown(self, requirements) -> list:
        """Return ``[{"topic": str, "priority": "high"|"medium"|"low"}, ...]``."""
        domain = self.detect_domain(requirements.subject)
        base = list(BANKS[domain])
        if requirements.level == "beginner":
            base.insert(0, FOUNDATIONS)
        elif requirements.level == "advanced":
            base = [ADVANCED] + base[1:]
        matched, result = set(), []
        for i, name in enumerate(base):
            hits = [d for d in requirements.difficult_topics if self._matches(d, name)]
            matched.update(hits)
            priority = "high" if hits else ("medium" if i < 3 else "low")
            result.append({"topic": name, "priority": priority})
        extras = [{"topic": d, "priority": "high"} for d in requirements.difficult_topics if d not in matched]
        result = extras + result
        log.info("Topic breakdown (%s domain): %d topics, %d high priority", domain, len(result),
                 sum(t["priority"] == "high" for t in result))
        return result
