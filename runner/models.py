"""Typed issue models shared by generation, validation, and delivery."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Mapping


BLOCK_ORDER = ("good_thing", "current_or_history", "tiny_fact")
CURRENT_HEADERS = {"on_this_day", "happening_now"}


def _normalise_block_lead(value: str) -> str:
    """Compare a label while ignoring emoji and punctuation."""

    return " ".join(
        "".join(character.lower() if character.isalnum() else " " for character in value).split()
    )


def _strip_block_lead(value: str, label: str) -> str:
    """Remove a duplicated first-line block label from model output."""

    lines = value.splitlines()
    if not lines or _normalise_block_lead(lines[0]) != _normalise_block_lead(label):
        return value
    return "\n".join(lines[1:]).lstrip()



class IssueFormatError(ValueError):
    """Raised when model output cannot be converted into a Kind of News issue."""


@dataclass(frozen=True)
class Source:
    block: str
    name: str
    descriptor: str
    url: str

    @classmethod
    def from_mapping(cls, raw: Mapping[str, Any]) -> "Source":
        required = ("block", "name", "descriptor", "url")
        missing = [key for key in required if not isinstance(raw.get(key), str)]
        if missing:
            raise IssueFormatError("Source fields must be strings: " + ", ".join(missing))
        return cls(
            block=raw["block"].strip(),
            name=raw["name"].strip(),
            descriptor=raw["descriptor"].strip(),
            url=raw["url"].strip(),
        )

    def to_dict(self) -> Dict[str, str]:
        return {
            "block": self.block,
            "name": self.name,
            "descriptor": self.descriptor,
            "url": self.url,
        }


@dataclass(frozen=True)
class NewsIssue:
    issue_id: str
    good_thing: str
    current_header: str
    current_or_history: str
    tiny_fact: str
    thought: str
    sources: List[Source]

    @classmethod
    def from_mapping(cls, raw: Mapping[str, Any]) -> "NewsIssue":
        required = (
            "issue_id",
            "good_thing",
            "current_header",
            "current_or_history",
            "tiny_fact",
            "thought",
            "sources",
        )
        missing = [key for key in required if key not in raw]
        if missing:
            raise IssueFormatError("Missing issue fields: " + ", ".join(missing))

        text_fields = required[:-1]
        bad_text = [key for key in text_fields if not isinstance(raw[key], str)]
        if bad_text:
            raise IssueFormatError("Issue fields must be strings: " + ", ".join(bad_text))
        if not isinstance(raw["sources"], list):
            raise IssueFormatError("sources must be an array")

        current_header = raw["current_header"].strip()
        sources = [Source.from_mapping(item) for item in raw["sources"]]
        return cls(
            issue_id=raw["issue_id"].strip(),
            good_thing=_strip_block_lead(raw["good_thing"].strip(), "Good thing"),
            current_header=current_header,
            current_or_history=_strip_block_lead(
                raw["current_or_history"].strip(),
                "Happening now" if current_header == "happening_now" else "On this day",
            ),
            tiny_fact=_strip_block_lead(raw["tiny_fact"].strip(), "Tiny fact"),
            thought=_strip_block_lead(raw["thought"].strip(), "Thought for the day"),
            sources=sources,
        )

    @classmethod
    def from_json_dict(cls, raw: Mapping[str, Any]) -> "NewsIssue":
        return cls.from_mapping(raw)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "issue_id": self.issue_id,
            "good_thing": self.good_thing,
            "current_header": self.current_header,
            "current_or_history": self.current_or_history,
            "tiny_fact": self.tiny_fact,
            "thought": self.thought,
            "sources": [source.to_dict() for source in self.sources],
        }

    def sources_for(self, block: str) -> Iterable[Source]:
        return (source for source in self.sources if source.block == block)

