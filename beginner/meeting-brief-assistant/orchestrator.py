"""Parallel + merge orchestration.

        parse request
        /           \\
 Agent A (tech)   Agent B (questions)     <- run at the same time (threads)
        \\           /
        Merger Agent -> 1-page cheat-sheet
"""
import time
from concurrent.futures import ThreadPoolExecutor
import threading

import config
from agents import TechStackAgent, QuestionsAgent, MergerAgent
from llm import LLMClient
from logger_setup import get_logger
from parser import parse_request
from state import MeetingState

log = get_logger()


class MeetingOrchestrator:
    def __init__(self):
        llm = LLMClient()
        log.info("Orchestrator ready | mode=%s", "LLM-assisted" if llm.available else "offline")
        self.tech_agent = TechStackAgent(llm)
        self.questions_agent = QuestionsAgent(llm)
        self.merger = MergerAgent(llm)

    # -- one meeting --------------------------------------------------------
    def brief(self, request: str) -> MeetingState:
        state = parse_request(request)
        ctx = state.context()
        log.info("INPUT    | %s", request)
        log.info("PARSED   | company=%s time=%s topic=%s category=%s warnings=%s",
                 state.company, state.time_label, state.topic, state.category, state.errors)

        start = time.perf_counter()
        with ThreadPoolExecutor(max_workers=2, thread_name_prefix="agent") as pool:
            jobs = {"TechStackAgent": pool.submit(self._timed, "TechStackAgent", self.tech_agent.run, ctx),
                    "QuestionsAgent": pool.submit(self._timed, "QuestionsAgent", self.questions_agent.run, ctx)}
            for name, fut in jobs.items():
                try:
                    result, secs = fut.result(timeout=config.AGENT_TIMEOUT)
                    state.timings[name] = secs
                    if name == "TechStackAgent":
                        state.tech = result
                    else:
                        state.questions = result
                except Exception as exc:               # one agent failing must not kill the brief
                    log.error("%s failed: %s", name, exc)
                    state.errors.append(f"{name} failed: {exc}")
        state.wall_time = time.perf_counter() - start
        log.info("PARALLEL | wall=%.2fs | sequential would take %.2fs",
                 state.wall_time, sum(state.timings.values()))

        if not state.questions:                        # graceful degradation
            log.warning("QuestionsAgent gave nothing; using the built-in question bank")
            state.questions = QuestionsAgent.fallback(ctx)

        state.brief = self.merger.run(state)
        log.info("MERGED   | %d lines, tech_points=%d, questions=%d",
                 state.brief.count("\n") + 1, len(state.tech.get("points", [])), len(state.questions))
        log.info("-" * 70)
        return state

    @staticmethod
    def _timed(name, fn, ctx):
        t0 = time.perf_counter()
        log.info("START    | %s", name)
        result = fn(ctx)
        secs = time.perf_counter() - t0
        log.info("DONE     | %s in %.2fs", name, secs)
        return result, secs

    # -- back-to-back meetings ----------------------------------------------
    def brief_day(self, requests: list) -> list:
        states = [self.brief(r) for r in requests if r.strip()]
        return sorted(states, key=lambda s: (s.time_minutes is None, s.time_minutes or 0))
