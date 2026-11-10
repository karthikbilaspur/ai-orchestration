
import os, json, logging
from state import LearnerState, QuizQuestion, QuizResult

logger = logging.getLogger(__name__)

try:
    import google.generativeai as genai
    genai.configure(api_key=os.getenv("GEMINI_API_KEY", ""))
    model = genai.GenerativeModel("gemini-1.5-flash")
    HAS_GEMINI = bool(os.getenv("GEMINI_API_KEY"))
except Exception as e:
    logger.warning(f"Gemini not configured, using fallback mode: {e}")
    model = None
    HAS_GEMINI = False

def call_llm(prompt: str) -> str:
    if not HAS_GEMINI or model is None:
        raise RuntimeError("GEMINI_API_KEY not set. Set it in .env or use MOCK_MODE=1")
    return model.generate_content(prompt).text

def _parse_json(text: str):
    cleaned = text.strip().replace("```json","").replace("```","").strip()
    return json.loads(cleaned)

def skill_assessment_agent(state: LearnerState, self_report: str) -> LearnerState:
    logger.info(f"SkillAssessment | topic={state.topic}")
    if not HAS_GEMINI:
        state.level = "beginner" if "nothing" in self_report.lower() or "no" in self_report.lower() else "intermediate"
        state.skill_summary = f"Mock assessment: {self_report[:120]}"
        return state
    prompt = f"""Topic: {state.topic}\nLearner says: "{self_report}"\nClassify as beginner/intermediate/advanced. Return JSON: {{"level": "...", "skill_summary": "..."}}"""
    data = _parse_json(call_llm(prompt))
    state.level = data["level"]; state.skill_summary = data["skill_summary"]
    return state

def planner_agent(state: LearnerState) -> LearnerState:
    logger.info(f"Planner | level={state.level}")
    if not HAS_GEMINI:
        state.roadmap = [f"{state.topic} - Fundamentals", f"{state.topic} - Core Concepts", f"{state.topic} - Practice", f"{state.topic} - Advanced Topics", f"{state.topic} - Final Review"]
        return state
    prompt = f"""Create a 5-step roadmap to learn {state.topic} for a {state.level} learner. Background: {state.skill_summary}. Return JSON: {{"roadmap": [...]}}"""
    state.roadmap = _parse_json(call_llm(prompt))["roadmap"]
    return state

def tutor_agent(state: LearnerState) -> LearnerState:
    current = state.roadmap[state.current_step] if state.roadmap else state.topic
    weak = state.history[-1].weak_topics if state.history else []
    logger.info(f"Tutor | step={state.current_step} topic={current} weak={weak}")
    if not HAS_GEMINI:
        state.tutor_explanation = f"## {current}\n\nThis is a mock explanation (set GEMINI_API_KEY for real AI). Focus: {', '.join(weak) if weak else 'core concepts'}.\n\n**Example:** Think of {current} like building blocks - start simple, then combine.\n\n**Try:** Explain it back in your own words."
        return state
    prompt = f"""Teach: {current} (Main: {state.topic}) Level: {state.level} Weak: {weak}. Explain clearly with 1 example and 1 analogy. Under 300 words."""
    state.tutor_explanation = call_llm(prompt)
    return state

def quiz_agent(state: LearnerState) -> LearnerState:
    current = state.roadmap[state.current_step] if state.roadmap else state.topic
    difficulty = "easy" if state.level == "beginner" else "medium"
    if state.history and state.history[-1].score < 0.6:
        difficulty = "easy"
    logger.info(f"Quiz | difficulty={difficulty}")
    if not HAS_GEMINI:
        state.quiz = [QuizQuestion(question=f"What is a key idea in {current}? (Q{i+1})", options=["Option A","Option B","Option C","Option D"], correct_index=0, topic=current, difficulty=difficulty) for i in range(5)]
        return state
    prompt = f"""Create 5 MCQs on {current} at {difficulty} difficulty. Return JSON list: [{{"question":"...","options":["a","b","c","d"],"correct_index":0,"topic":"{current}","difficulty":"{difficulty}"}}]"""
    data = _parse_json(call_llm(prompt))
    state.quiz = [QuizQuestion(**q) for q in data]
    return state

def evaluator_agent(state: LearnerState, user_answers: list[int]) -> LearnerState:
    correct = sum(1 for q,a in zip(state.quiz, user_answers) if q.correct_index == a)
    score = correct / len(state.quiz) if state.quiz else 0
    weak = list(set(q.topic for q,a in zip(state.quiz, user_answers) if q.correct_index != a))
    logger.info(f"Evaluator | score={score:.2f} weak={weak}")
    if not HAS_GEMINI:
        feedback = "Good effort! Keep practicing weak areas." if score < 0.7 else "Excellent! Ready for next topic."
        next_action = "revise" if score < 0.7 else "next_topic"
    else:
        prompt = f"""Learner scored {score} on {state.topic}. Wrong: {weak}. Give 2 lines feedback and decide next_action revise if <0.7 else next_topic. Return JSON: {{"feedback":"...","next_action":"..."}}"""
        d = _parse_json(call_llm(prompt)); feedback=d["feedback"]; next_action=d["next_action"]
    state.history.append(QuizResult(score=score, weak_topics=weak, feedback=feedback, next_action=next_action))
    return state
