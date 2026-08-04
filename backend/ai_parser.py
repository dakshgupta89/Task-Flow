"""AI quick-add mock parser — deterministic, rule-based, zero network calls.

Simulates what an LLM response would contain, following the exact algorithm
specified in Section 3. The prompt is constructed with the standard role-based
structure (system + user messages) even though the mock does the parsing locally.
"""

import re
from dataclasses import dataclass
from typing import Optional

PRIORITY_KEYWORDS = ["urgent", "asap", "whenever", "low priority"]

# "next <weekday>" phrases, checked Monday-to-Sunday
NEXT_WEEKDAY_PHRASES = [
    "next monday",
    "next tuesday",
    "next wednesday",
    "next thursday",
    "next friday",
    "next saturday",
    "next sunday",
]

# Bare weekday names, checked Monday-to-Sunday
BARE_WEEKDAYS = [
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
    "sunday",
]

DATE_KEYWORDS = ["today", "tomorrow", "next week"] + NEXT_WEEKDAY_PHRASES + BARE_WEEKDAYS


@dataclass
class ParsedTask:
    title: str
    priority: str
    due_date_hint: Optional[str]


def build_prompt(description: str) -> list[dict[str, str]]:
    """Construct the role-based message list (system + user) for the parser.

    This mirrors the standard LLM messaging structure so the code stays the same
    whether the mock or a real model answers.
    """
    system_instruction = (
        "You are a task-parsing assistant. Given a free-text description of a task, "
        "extract three fields: a clean title, a priority (one of 'low', 'medium', 'high'), "
        "and an optional due_date_hint (a raw phrase like 'tomorrow' or 'next friday', or null). "
        "Remove any priority keywords ('urgent', 'asap', 'whenever', 'low priority') and any "
        "matched date phrases from the title. If the remaining title is blank, use 'Untitled task'. "
        "Respond as JSON with keys: title, priority, due_date_hint."
    )
    user_message = description
    return [
        {"role": "system", "content": system_instruction},
        {"role": "user", "content": user_message},
    ]


def _determine_priority(lower_text: str) -> str:
    """Determine priority by checking keyword groups in exact order."""
    if "urgent" in lower_text or "asap" in lower_text:
        return "high"
    if "whenever" in lower_text or "low priority" in lower_text:
        return "low"
    return "medium"


def _determine_due_date(lower_text: str) -> tuple[Optional[str], list[str]]:
    """Determine the due-date hint. Returns (hint, matched_spans).

    matched_spans contains the exact matched keyword/phrase text (lower-case)
    for title-stripping purposes.
    """
    # Check "today", "tomorrow", "next week" first
    for kw in ["today", "tomorrow", "next week"]:
        if kw in lower_text:
            # Find all occurrences for title stripping
            spans = []
            idx = 0
            while True:
                pos = lower_text.find(kw, idx)
                if pos == -1:
                    break
                spans.append(kw)
                idx = pos + len(kw)
            return kw, spans

    # Check "next <weekday>" phrases (Monday-to-Sunday order)
    for phrase in NEXT_WEEKDAY_PHRASES:
        if phrase in lower_text:
            spans = []
            idx = 0
            while True:
                pos = lower_text.find(phrase, idx)
                if pos == -1:
                    break
                spans.append(phrase)
                idx = pos + len(phrase)
            return phrase, spans

    # Check bare weekday names (Monday-to-Sunday order)
    for day in BARE_WEEKDAYS:
        if day in lower_text:
            spans = []
            idx = 0
            while True:
                pos = lower_text.find(day, idx)
                if pos == -1:
                    break
                spans.append(day)
                idx = pos + len(day)
            return day, spans

    return None, []


def _strip_spans(original: str, lower_text: str, keywords: list[str]) -> str:
    """Remove every occurrence of each keyword from the original text.

    Keywords are matched case-insensitively against the lower-cased text, but the
    corresponding span is removed from the original-cased text.
    """
    # Build a list of (start, end) positions to remove, using lower-cased text
    spans_to_remove = []
    for kw in keywords:
        if not kw:
            continue
        idx = 0
        while True:
            pos = lower_text.find(kw, idx)
            if pos == -1:
                break
            spans_to_remove.append((pos, pos + len(kw)))
            idx = pos + len(kw)

    # Sort spans by start position
    spans_to_remove.sort(key=lambda s: s[0])

    # Build the result by removing spans from the original text
    result = []
    prev_end = 0
    for start, end in spans_to_remove:
        # Avoid overlapping spans — skip if this span starts before previous end
        if start < prev_end:
            continue
        result.append(original[prev_end:start])
        prev_end = end
    result.append(original[prev_end:])

    return "".join(result)


def mock_parse_description(description: str) -> ParsedTask:
    """Parse a free-text description into a structured task (deterministic, rule-based).

    Follows the exact algorithm from Section 3, Task 3.
    """
    lower_text = description.lower()

    # (b) Priority
    priority = _determine_priority(lower_text)

    # (c) Due-date hint
    due_date_hint, date_spans = _determine_due_date(lower_text)

    # (d) Title — strip priority keywords and matched date phrases from original
    keywords_to_strip = [kw for kw in PRIORITY_KEYWORDS if kw in lower_text]
    keywords_to_strip += date_spans

    stripped = _strip_spans(description, lower_text, keywords_to_strip)
    title = stripped.strip()

    if not title or title.isspace():
        title = "Untitled task"

    return ParsedTask(title=title, priority=priority, due_date_hint=due_date_hint)


def parse_task_from_description(description: str) -> dict:
    """Full parse pipeline: build prompt, run mock, return dict for TaskResponse validation.

    In an optional real-LLM path (behind USE_REAL_LLM flag), the prompt from
    build_prompt() would be sent to a model instead. With the mock active, the
    same structure is used but the parsing is deterministic.
    """
    # Build the role-based prompt (always constructed for structural consistency)
    _prompt = build_prompt(description)

    # Run the mock parser
    parsed = mock_parse_description(description)

    return {
        "title": parsed.title,
        "priority": parsed.priority,
        "due_date": parsed.due_date_hint,
    }
