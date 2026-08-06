sed: --: No such file or directory
"""Typed issue models shared by generation, validation, and delivery."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Mapping


BLOCK_ORDER = ("good_thing", "current_or_history", "tiny_fact")
CURRENT_HEADERS = {"on_this_day", "happening_now"}


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

        sources = [Source.from_mapping(item) for item in raw["sources"]]
        return cls(
            issue_id=raw["issue_id"].strip(),
            good_thing=raw["good_thing"].strip(),
            current_header=raw["current_header"].strip(),
            current_or_history=raw["current_or_history"].strip(),
            tiny_fact=raw["tiny_fact"].strip(),
            thought=raw["thought"].strip(),
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

