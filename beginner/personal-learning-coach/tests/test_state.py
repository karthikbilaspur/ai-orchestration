
from state import LearnerState, QuizQuestion, QuizResult
def test_quiz_question_validation():
    q = QuizQuestion(question="Q?", options=["a","b"], correct_index=0, topic="T", difficulty="easy")
    assert q.correct_index == 0
def test_default_state():
    s = LearnerState(topic="Math")
    assert s.current_step == 0 and s.attempts == 0 and s.history == []
