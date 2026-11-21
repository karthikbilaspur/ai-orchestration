"""Quiz agent: generates practice questions that match the learner's assessment preference."""
from __future__ import annotations

import logging

log = logging.getLogger(__name__)

TEMPLATES = (
    "Explain {topic} in your own words and give one practical example from {subject}.",
    "What are common mistakes when working with {topic}, and how can you avoid them?",
    "How does {topic} connect to another part of {subject} you have studied?",
    "Outline a small problem that applies {topic} and justify each step.",
    "Teach {topic} to a beginner in five sentences. What would you leave out, and why?",
)
MAX_COVERS_PER_SESSION = 5


class QuizGenerator:
    def generate(self, req, sessions: list) -> list:
        questions, counter = [], 0
        for s in sessions:
            if s["kind"] == "study":
                if req.assessment != "daily quizzes":
                    continue
                topics, label = s["covers"], "daily quiz"
            else:
                topics = s["covers"][:MAX_COVERS_PER_SESSION]
                label = "weekly assessment" if s["kind"] == "assessment" else "revision check"
            for topic in topics:
                text = TEMPLATES[counter % len(TEMPLATES)].format(topic=topic, subject=req.subject)
                questions.append({"session_index": s["index"], "day": s["day"], "topic": topic,
                                  "kind": label, "question": text})
                counter += 1
        log.info("Generated %d practice questions", len(questions))
        return questions
