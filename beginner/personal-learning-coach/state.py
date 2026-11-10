
from pydantic import BaseModel, Field
from typing import List, Literal

class QuizQuestion(BaseModel):
    question: str
    options: List[str]
    correct_index: int
    topic: str
    difficulty: Literal["easy", "medium", "hard"]

class QuizResult(BaseModel):
    score: float
    weak_topics: List[str]
    feedback: str
    next_action: Literal["revise", "next_topic"]

class LearnerState(BaseModel):
    topic: str
    level: Literal["beginner", "intermediate", "advanced"] = "beginner"
    skill_summary: str = ""
    roadmap: List[str] = []
    current_step: int = 0
    tutor_explanation: str = ""
    quiz: List[QuizQuestion] = []
    history: List[QuizResult] = []
    attempts: int = 0
