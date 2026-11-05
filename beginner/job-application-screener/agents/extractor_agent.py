"""Agent 1: list the skills found in the resume (negation-aware)."""
import json
import re
from llm import LLMClient
from skills_taxonomy import find_skills, affirmative
from state import ScreeningState

SECTION_RE = re.compile(
    r"(?:^|(?<=[\s.]))(name|technical skills|skills?|projects?|work experience|"
    r"experience|education|summary|certifications?)\s*:", re.I | re.M)

LLM_PROMPT = ('List the skills in this resume. Reply with ONLY JSON: {"skills": ["..."]}. '
              "Only include skills the candidate actually has. Never include skills the "
              "resume says they lack.")


def parse_sections(text: str) -> dict:
    matches = list(SECTION_RE.finditer(text))
    sections = {}
    for i, m in enumerate(matches):
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        label = m.group(1).lower()
        key = ("skills" if "skill" in label else "projects" if label.startswith("project")
               else "experience" if "experience" in label else label)
        sections[key] = (sections.get(key, "") + " " + text[m.end():end]).strip()
    return sections


def _tokens_to_skills(tokens):
    skills = []
    for token in tokens:
        token = token.strip(" .")
        if not token or len(token) > 40:
            continue
        found, negated = find_skills(token)
        if found:
            skills += sorted(found, key=found.get)
        elif not negated:
            skills.append(token[:1].upper() + token[1:])
    return skills


class ExtractorAgent:
    def __init__(self, llm: LLMClient = None):
        self.llm = llm or LLMClient()

    def run(self, state: ScreeningState) -> ScreeningState:
        text = state.resume.strip()
        if not text:
            state.status, state.reason = "Rejected", "Empty resume"
            state.match_level, state.stopped_early = "Rejected", True
            return state

        state.sections = parse_sections(text)
        name = re.split(r"[.\n]", state.sections.get("name", ""))[0].strip()
        state.candidate_name = name or "Unknown"

        # 1) skills the candidate wrote in the Skills section
        listed = _tokens_to_skills(re.split(r"[,;/|•·&\n]+|\s+and\s+",
                                            state.sections.get("skills", "")))
        # 2) skills mentioned anywhere else (projects, experience), skipping denied ones
        found, negated = find_skills(text)
        skills = listed + sorted(found, key=found.get)

        # 3) optional LLM, but its answers must really appear in the resume
        if self.llm.available:
            try:
                raw = self.llm.complete(LLM_PROMPT, text, max_tokens=200)
                data = json.loads(re.sub(r"```json|```", "", raw).strip())
                extra = [s for s in data.get("skills", [])
                         if isinstance(s, str) and affirmative(re.escape(s), text)]
                skills += _tokens_to_skills(extra)
            except Exception as exc:
                state.errors.append(f"extractor LLM failed, using rules: {exc}")

        state.skills = list(dict.fromkeys(skills))
        state.negated = sorted(negated)
        return state
