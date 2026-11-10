
from state import LearnerState
from agents import skill_assessment_agent, planner_agent, tutor_agent, quiz_agent, evaluator_agent
from orchestrator import run_learning_loop

def test_full_loop_mock():
    # Mock mode (no GEMINI_API_KEY) should still work
    state = LearnerState(topic="Python")
    state = skill_assessment_agent(state, "Nothing yet")
    assert state.level in ["beginner","intermediate","advanced"]
    state = planner_agent(state)
    assert len(state.roadmap) == 5
    state = tutor_agent(state); state = quiz_agent(state)
    assert len(state.quiz) == 5
    assert state.tutor_explanation

def test_evaluator_revise():
    state = LearnerState(topic="Python", roadmap=["A","B"])
    state = tutor_agent(state); state = quiz_agent(state)
    # Answer all wrong -> should revise
    state, action = run_learning_loop(state, [1]*len(state.quiz))
    assert action == "revise"
    assert state.history[-1].score < 0.7

def test_evaluator_next_topic():
    state = LearnerState(topic="Python", roadmap=["A","B"])
    state = tutor_agent(state); state = quiz_agent(state)
    # Answer all correct (correct_index=0 in mock) -> next_topic
    state, action = run_learning_loop(state, [0]*len(state.quiz))
    assert action == "next_topic"
    assert state.current_step == 1

def test_state_serialization():
    s = LearnerState(topic="Biology")
    j = s.model_dump_json()
    s2 = LearnerState.model_validate_json(j)
    assert s2.topic == "Biology"
