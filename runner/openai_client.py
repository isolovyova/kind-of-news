"""OpenAI Responses API gateway with injectable responses for tests."""

from __future__ import annotations

import json
import re
from typing import Any, Dict, Iterable, Optional, Set, Tuple

from .models import NewsIssue
from .prompts import compose_prompt, issue_format, research_format, research_prompt
from .validate import validate_issue


class OpenAIRuntimeError(RuntimeError):
    """Raised when the Responses API cannot produce usable structured output."""


def _as_dict(value: Any) -> Any:
    if isinstance(value, dict):
        return value
    if hasattr(value, "model_dump"):
        return value.model_dump()
    if hasattr(value, "to_dict"):
        return value.to_dict()
    return value


def _walk(value: Any) -> Iterable[Any]:
    value = _as_dict(value)
    yield value
    if isinstance(value, dict):
        for child in value.values():
            yield from _walk(child)
    elif isinstance(value, (list, tuple)):
        for child in value:
            yield from _walk(child)


def response_text(response: Any) -> str:
    text = getattr(response, "output_text", None)
    if isinstance(text, str) and text.strip():
        return text.strip()
    response_dict = _as_dict(response)
    if isinstance(response_dict, dict) and isinstance(response_dict.get("output_text"), str):
        return response_dict["output_text"].strip()
    for item in _walk(response_dict):
        if isinstance(item, dict) and item.get("type") in {"output_text", "text"}:
            candidate = item.get("text")
            if isinstance(candidate, str) and candidate.strip():
                return candidate.strip()
    raise OpenAIRuntimeError("Responses API returned no output text")


def parse_json_response(response: Any) -> Dict[str, Any]:
    raw = response_text(response)
    try:
        value = json.loads(raw)
    except json.JSONDecodeError as exc:
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if not match:
            raise OpenAIRuntimeError("Responses API output was not valid JSON") from exc
        try:
            value = json.loads(match.group(0))
        except json.JSONDecodeError as nested_exc:
            raise OpenAIRuntimeError("Responses API output was not valid JSON") from nested_exc
    if not isinstance(value, dict):
        raise OpenAIRuntimeError("Responses API JSON output must be an object")
    return value


def extract_citation_urls(response: Any) -> Set[str]:
    """Collect URLs from web-search annotations and structured research output."""

    urls: Set[str] = set()
    for item in _walk(response):
        if not isinstance(item, dict):
            continue
        url = item.get("url")
        if isinstance(url, str) and url.startswith("https://"):
            urls.add(url)
        sources = item.get("sources")
        if isinstance(sources, list):
            for source in sources:
                if isinstance(source, dict) and isinstance(source.get("url"), str):
                    if source["url"].startswith("https://"):
                        urls.add(source["url"])
    return urls


class ResponsesClient:
    """Small wrapper around the official OpenAI Python SDK."""

    def __init__(self, api_key: str, model: str, sdk_client: Optional[Any] = None):
        if not api_key:
            raise OpenAIRuntimeError("OPENAI_API_KEY is required")
        self.model = model
        if sdk_client is not None:
            self.client = sdk_client
            return
        try:
            from openai import OpenAI
        except ImportError as exc:  # pragma: no cover - exercised in CI install.
            raise OpenAIRuntimeError("Install the openai package to use the API runtime") from exc
        self.client = OpenAI(api_key=api_key)

    def _create(self, prompt: str, output_name: str, output_schema: Dict[str, Any], search: bool) -> Any:
        kwargs: Dict[str, Any] = {
            "model": self.model,
            "input": prompt,
            "text": {"format": output_schema},
            "store": False,
        }
        if search:
            kwargs["tools"] = [{"type": "web_search"}]
        try:
            return self.client.responses.create(**kwargs)
        except Exception as exc:  # SDK exceptions vary by installed SDK version.
            raise OpenAIRuntimeError("Responses API request failed") from exc

    def generate_issue(
        self,
        skill_text: str,
        issue_date: str,
        weekday: str,
    ) -> Tuple[NewsIssue, Set[str]]:
        research_response = self._create(
            research_prompt(skill_text, issue_date, weekday),
            "kind_of_news_research",
            research_format(),
            search=True,
        )
        research = parse_json_response(research_response)
        citation_urls = extract_citation_urls(research_response)
        citation_urls.update(extract_citation_urls(research))
        compose_response = self._create(
            compose_prompt(skill_text, issue_date, weekday, research),
            "kind_of_news_issue",
            issue_format(),
            search=False,
        )
        issue = NewsIssue.from_mapping(parse_json_response(compose_response))
        validate_issue(issue, expected_date=issue_date, citation_urls=citation_urls)
        return issue, citation_urls
