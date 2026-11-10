
import streamlit as st, sqlite3, logging, os
from dotenv import load_dotenv
load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", handlers=[logging.FileHandler("logs/app.log"), logging.StreamHandler()])
from state import LearnerState
from agents import skill_assessment_agent, planner_agent, tutor_agent, quiz_agent
from orchestrator import run_learning_loop

st.set_page_config(page_title="AI Personal Learning Coach", page_icon="🎓")
st.title("🎓 AI Personal Learning Coach")
st.caption("Adaptive orchestration • Skill Assessment → Planner → Tutor → Quiz → Evaluator → Feedback Loop")

conn = sqlite3.connect("learning.db", check_same_thread=False)
conn.execute("CREATE TABLE IF NOT EXISTS sessions (topic TEXT PRIMARY KEY, state TEXT)")
conn.commit()

if "state" not in st.session_state: st.session_state.state = None

# Resume
saved = conn.execute("SELECT topic FROM sessions").fetchall()
if saved:
    with st.sidebar:
        st.subheader("📂 Resume Session")
        choice = st.selectbox("Saved topics", ["-- New --"] + [r[0] for r in saved])
        if choice != "-- New --" and st.button("Load"):
            row = conn.execute("SELECT state FROM sessions WHERE topic=?", (choice,)).fetchone()
            st.session_state.state = LearnerState.model_validate_json(row[0]); st.rerun()

topic = st.text_input("What do you want to learn?", placeholder="e.g. Python, Photosynthesis, French verbs")
self_report = st.text_area("What do you already know about it?", "Nothing yet")
if st.button("🚀 Start Learning") and topic:
    with st.spinner("Assessing your level & building your roadmap..."):
        state = LearnerState(topic=topic)
        state = skill_assessment_agent(state, self_report)
        state = planner_agent(state)
        state = tutor_agent(state); state = quiz_agent(state)
        st.session_state.state = state
        conn.execute("INSERT OR REPLACE INTO sessions VALUES (?, ?)", (topic, state.model_dump_json())); conn.commit()

if st.session_state.state:
    state: LearnerState = st.session_state.state
    st.subheader(f"Step {state.current_step+1}/{len(state.roadmap)}: {state.roadmap[state.current_step]}")
    st.write(f"**Level:** {state.level} | **Background:** {state.skill_summary}")
    st.progress(state.current_step / max(1, len(state.roadmap)))
    st.markdown(state.tutor_explanation)
    st.divider(); st.subheader("📝 Quiz")
    answers=[]
    for i,q in enumerate(state.quiz):
        ans = st.radio(q.question, q.options, key=f"q{i}_{state.current_step}_{state.attempts}")
        answers.append(q.options.index(ans))
    if st.button("Submit Quiz"):
        state, action = run_learning_loop(state, answers)
        st.session_state.state = state
        conn.execute("INSERT OR REPLACE INTO sessions VALUES (?, ?)", (state.topic, state.model_dump_json())); conn.commit()
        last = state.history[-1]
        st.success(f"Score: {last.score*100:.0f}% — {last.feedback}")
        if action=="revise": st.warning(f"Let's revise. Weak areas: {', '.join(last.weak_topics) if last.weak_topics else '—'}")
        elif action=="completed": st.balloons(); st.success("🎉 Roadmap completed!")
        else: st.info("Great! Moving to next topic...")
        st.rerun()
    if st.session_state.state.history:
        with st.expander("📊 History"):
            for h in st.session_state.state.history:
                st.write(f"Score {h.score*100:.0f}% | {h.next_action} | {h.feedback}")
