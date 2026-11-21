"""Transcript parser: turns raw text into attributed sentences.

Supported line shapes (all optional parts can be mixed)::

    [00:01:23] Maya: We decided to ship on Friday.
    Maya: Sam will update the docs.
    Decision: use option B
    Action: Alex to prepare the announcement
    plain text with no speaker

Each sentence is a dict: ``index, speaker, timestamp, label, text``.
"""
from __future__ import annotations

import re
from collections import Counter

DECISION_LABELS = {"decision", "decisions"}
ACTION_LABELS = {"action", "action item", "action items", "todo", "to-do", "to do", "ai",
                 "next step", "next steps"}
NOTE_LABELS = {"note", "notes", "agenda", "summary"}
ALL_LABELS = DECISION_LABELS | ACTION_LABELS | NOTE_LABELS

_LINE_RE = re.compile(
    r"^\s*(?:[-*\u2022]\s+)?"
    r"(?:\[?(?P<ts>\d{1,2}:\d{2}(?::\d{2})?)\]?\s*[-\u2013]?\s*)?"
    r"(?:(?P<speaker>[A-Z][\w.'\u2019-]*(?:\s+[A-Z][\w.'\u2019-]*){0,2})\s*:\s*)?"
    r"(?P<text>.*?)\s*$"
)
_LABEL_RE = re.compile(r"^(?P<label>[A-Za-z][A-Za-z -]{0,20}?)\s*:\s*(?P<rest>\S.*)$")
_ABBR = re.compile(r"\b(?:e\.g|i\.e|etc|vs|dr|mr|mrs|ms|prof|inc|ltd)\.", re.IGNORECASE)
_SPLIT_RE = re.compile(r"(?<=[.!?])\s+(?=[\"'(\[]?[A-Z0-9])")


def split_sentences(text: str) -> list:
    protected = _ABBR.sub(lambda m: m.group(0).replace(".", "\u0000"), text)
    parts = _SPLIT_RE.split(protected)
    return [p.replace("\u0000", ".").strip() for p in parts if p.strip()]


def name_aliases(names) -> set:
    """Lower-case full names and name parts, used to recognise speaker labels."""
    aliases = set()
    for name in names or []:
        low = name.lower().strip()
        aliases.add(low)
        aliases.update(part for part in re.split(r"\s+", low) if len(part) >= 2)
    return aliases


def parse_transcript(text: str, known_names=None) -> list:
    rows = []
    for raw in text.splitlines():
        m = _LINE_RE.match(raw)
        if not m:
            continue
        speaker, body, ts, label = m.group("speaker"), m.group("text"), m.group("ts"), None
        if speaker and speaker.lower() in ALL_LABELS:
            label, speaker = speaker.lower(), None
        if not label:  # a speaker may also prefix a labelled line: "Priya: Action: ..."
            lm = _LABEL_RE.match(body)
            if lm and lm.group("label").lower() in ALL_LABELS:
                label, body = lm.group("label").lower(), lm.group("rest")
        body = " ".join(body.split())
        if not body:
            continue
        rows.append({"ts": ts, "speaker": speaker, "text": body, "label": label})

    counts = Counter(r["speaker"] for r in rows if r["speaker"])
    aliases = name_aliases(known_names)
    for r in rows:
        sp = r["speaker"]
        if sp and aliases and sp.lower() not in aliases and counts[sp] < 2:
            r["text"], r["speaker"] = f"{sp}: {r['text']}", None  # probably not a speaker label

    sentences = []
    for r in rows:
        for part in split_sentences(r["text"]):
            sentences.append({"index": len(sentences), "speaker": r["speaker"], "timestamp": r["ts"],
                              "label": r["label"], "text": part})
    return sentences


def ensure_sentences(transcript, known_names=None) -> list:
    """Accept raw text or an already-parsed sentence list."""
    return parse_transcript(transcript, known_names) if isinstance(transcript, str) else list(transcript)


def participant_stats(sentences: list) -> dict:
    stats: dict = {}
    for s in sentences:
        if s["speaker"]:
            entry = stats.setdefault(s["speaker"], {"sentences": 0, "words": 0})
            entry["sentences"] += 1
            entry["words"] += len(s["text"].split())
    return stats
