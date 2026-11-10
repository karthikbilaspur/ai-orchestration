
import logging
from state import LearnerState
from agents import evaluator_agent, tutor_agent, quiz_agent
logger = logging.getLogger(__name__)

def run_learning_loop(state: LearnerState, user_answers: list[int] | None = None):
    """Returns (state, action) where action in revise/next_topic/completed/waiting"""
    if user_answers is None:
        return state, "waiting"
    state = evaluator_agent(state, user_answers)
    last = state.history[-1]
    logger.info(f"Orchestrator | next_action={last.next_action} step={state.current_step}")
    if last.next_action == "revise":
        state.attempts += 1
        state = tutor_agent(state); state = quiz_agent(state)
        return state, "revise"
    else:
        state.current_step += 1; state.attempts = 0
        if state.current_step >= len(state.roadmap):
            return state, "completed"
        state = tutor_agent(state); state = quiz_agent(state)
        return state, "next_topic"
