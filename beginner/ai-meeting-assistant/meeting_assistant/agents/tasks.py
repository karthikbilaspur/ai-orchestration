"""Task Assignment agent: extracts action items, owners, deadlines and priority."""
from __future__ import annotations

import logging
import re
from datetime import date

from meeting_assistant.dates import extract_deadline
from meeting_assistant.parser import ACTION_LABELS, ensure_sentences, name_aliases

log = logging.getLogger(__name__)

CUE_RE = re.compile(
    r"(?:\bwill(?!\s+be\b)|\bshall(?!\s+be\b)|'ll\b|\u2019ll\b|\b(?:needs?|has|have)\s+to\b|"
    r"\b(?:is|are)\s+going\s+to\b|['\u2019]m\s+going\s+to\b|\bshould\b|\bmust\b|"
    r"\bvolunteer(?:s|ed)?\s+to\b|\bagreed\s+to\b|\bto\s+follow\s+up\b|\bfollow\s+up\b)", re.I)
REQUEST_RE = re.compile(r"^(?:[\w,]+\s+)?(?P<name>[A-Z][\w'\u2019-]*(?:\s+[A-Z][\w'\u2019-]*)?),?\s+"
                        r"(?:can|could|would|will)\s+you\b")
LABEL_OWNER_RE = re.compile(
    r"^(?P<owner>[A-Z][\w'\u2019-]+(?:\s*(?:,|and|&)\s*[A-Z][\w'\u2019-]+)*)\s+"
    r"(?:to|will|should|must|needs?\s+to)\b")
FIRST_PERSON_RE = re.compile(r"\bI\s*$")
GROUP_RE = re.compile(r"\b(?:we|everyone|team|all)\s*$", re.I)
HIGH_RE = re.compile(r"\b(urgent|asap|critical|immediately|blocker|top priority|high priority)\b", re.I)
LOW_RE = re.compile(r"\b(low priority|nice to have|when (?:you )?(?:can|possible)|if time permits)\b", re.I)
UNASSIGNED = "Unassigned"


class TaskAssignmentAgent:
    def _alias_map(self, attendees) -> dict:
        full = {a.lower(): a for a in attendees}
        parts: dict = {}
        for a in attendees:
            for p in re.split(r"\s+", a.lower()):
                if len(p) >= 2:
                    parts.setdefault(p, set()).add(a)
        for p, owners in parts.items():
            if len(owners) == 1 and p not in full:  # ambiguous first names are ignored
                full[p] = next(iter(owners))
        return full

    def _find_names(self, text: str, alias_map: dict) -> list:
        hits = []
        for alias, canonical in alias_map.items():
            for m in re.finditer(r"\b" + re.escape(alias) + r"\b", text, re.I):
                hits.append((m.start(), canonical))
        ordered, seen = [], set()
        for _, name in sorted(hits):
            if name not in seen:
                seen.add(name)
                ordered.append(name)
        return ordered

    def _canonical(self, raw: str, alias_map: dict) -> str:
        names = [n.strip() for n in re.split(r",|\band\b|&", raw) if n.strip()]
        return " & ".join(alias_map.get(n.lower(), n) for n in names[:3])

    def extract(self, transcript, attendees=None, assign: bool = False, reference_date: date | None = None) -> list:
        attendees = list(attendees or [])
        ref = reference_date or date.today()
        sentences = ensure_sentences(transcript, attendees)
        alias_map = self._alias_map(attendees)
        tasks, seen = [], set()
        for s in sentences:
            text = s["text"]
            owner, source = None, None
            req = REQUEST_RE.match(text) if text.endswith("?") else None
            if req:
                owner, source = self._canonical(req.group("name"), alias_map), "request"
            elif s["label"] in ACTION_LABELS:
                lo = LABEL_OWNER_RE.match(text)
                owner, source = (self._canonical(lo.group("owner"), alias_map) if lo else None), "label"
            elif not text.endswith("?"):
                cue = CUE_RE.search(text)
                if not cue:
                    continue
                source = "commitment"
                before = text[:cue.start()]
                names = self._find_names(before, alias_map)
                if names:
                    owner = " & ".join(names[:2])
                elif FIRST_PERSON_RE.search(before.strip()) and s["speaker"]:
                    owner = s["speaker"]
                elif GROUP_RE.search(before.strip()):
                    owner = "Team"
            else:
                continue
            key = text.lower()
            if key in seen:
                continue
            seen.add(key)
            phrase, due = extract_deadline(text, ref)
            priority = "high" if HIGH_RE.search(text) else ("low" if LOW_RE.search(text) else "normal")
            tasks.append({"id": f"A{len(tasks) + 1}", "task": text,
                          "owner": (owner or UNASSIGNED) if assign else UNASSIGNED,
                          "due_text": phrase, "due_date": due, "priority": priority,
                          "speaker": s["speaker"], "timestamp": s["timestamp"], "source": source})
        log.info("Extracted %d action item(s)", len(tasks))
        return tasks
