"""Host-neutral orchestration for the normal first-user setup confirmation.

Host integrations provide the recurring-schedule and delivery adapters. This
module keeps the ordering and user-facing completion contract testable without
owning credentials, network calls, or a scheduler implementation.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from typing import Protocol, Sequence
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from .delivery.base import DeliveryResult
from .models import NewsIssue
from .render import render_markdown
from .validate import validate_issue


class SetupFlowError(RuntimeError):
    """Raised when the confirmed setup flow cannot complete safely."""


class SetupNotConfirmedError(SetupFlowError):
    """Raised when delivery is attempted without final user confirmation."""


class SetupIncompleteError(SetupFlowError):
    """Raised when schedule activation or the immediate send is unverified."""


@dataclass(frozen=True)
class ScheduleActivation:
    """Verified result returned by a recurring-schedule adapter."""

    active: bool
    next_run: datetime


class RecurringScheduler(Protocol):
    def activate(
        self,
        *,
        channel: str,
        days: Sequence[str],
        delivery_time: str,
        timezone: str,
        first_issue_date: str,
        next_run: datetime,
    ) -> ScheduleActivation:
        """Activate subsequent delivery and return its verified next run."""


class ChannelDelivery(Protocol):
    def send(self, issue: NewsIssue) -> DeliveryResult:
        """Send one already validated issue through the selected channel."""


@dataclass(frozen=True)
class SetupResult:
    """Verified normal-setup outcome and rendered first issue."""

    issue: NewsIssue
    rendered_issue: str
    schedule: ScheduleActivation
    delivery: DeliveryResult
    message: str


_WEEKDAYS = {
    "monday": 0,
    "tuesday": 1,
    "wednesday": 2,
    "thursday": 3,
    "friday": 4,
    "saturday": 5,
    "sunday": 6,
}


def _parse_delivery_time(value: str) -> time:
    try:
        return datetime.strptime(value, "%H:%M").time()
    except ValueError as exc:
        raise SetupFlowError("delivery time must use HH:MM") from exc


def _next_scheduled_run(
    after_date: date,
    days: Sequence[str],
    delivery_time: str,
    timezone: str,
) -> datetime:
    normalized_days = [day.strip().lower() for day in days]
    unknown = sorted(set(normalized_days) - set(_WEEKDAYS))
    if not normalized_days or unknown:
        raise SetupFlowError("schedule.days contains an unknown weekday")
    try:
        zone = ZoneInfo(timezone)
    except ZoneInfoNotFoundError as exc:
        raise SetupFlowError("Unknown timezone: %s" % timezone) from exc

    local_time = _parse_delivery_time(delivery_time)
    target_weekdays = {_WEEKDAYS[day] for day in normalized_days}
    for offset in range(1, 8):
        candidate = after_date + timedelta(days=offset)
        if candidate.weekday() in target_weekdays:
            return datetime.combine(candidate, local_time, tzinfo=zone)
    raise SetupFlowError("Could not determine the next scheduled delivery")


def _join_days(days: Sequence[str]) -> str:
    labels = [day.strip().capitalize() for day in days]
    if len(labels) == 1:
        return labels[0]
    if len(labels) == 2:
        return "%s and %s" % (labels[0], labels[1])
    return "%s, and %s" % (", ".join(labels[:-1]), labels[-1])


def _destination_line(channel: str, issue_id: str) -> str:
    if channel == "gmail":
        return "Check your email for Kind of News #%s." % issue_id
    return "Check your %s channel for Kind of News #%s." % (channel, issue_id)


def complete_confirmed_setup(
    *,
    channel: str,
    days: Sequence[str],
    timezone: str,
    delivery_time: str,
    publication_date: date,
    issue: NewsIssue,
    confirmed: bool,
    scheduler: RecurringScheduler,
    delivery: ChannelDelivery,
) -> SetupResult:
    """Validate, activate subsequent delivery, and send issue #1 once confirmed.

    The schedule is activated before the immediate first send, matching the
    normal setup contract. No adapter is called until ``confirmed`` is true,
    and no success result is returned unless both adapter results are verified.
    """

    if not confirmed:
        raise SetupNotConfirmedError("Final confirmation is required before delivery")

    normalized_channel = channel.strip().lower()
    if not normalized_channel:
        raise SetupFlowError("A delivery channel is required")

    expected_date = publication_date.isoformat()
    validate_issue(issue, expected_date=expected_date)
    rendered_issue = render_markdown(issue)
    expected_next_run = _next_scheduled_run(
        publication_date,
        days,
        delivery_time,
        timezone,
    )

    schedule = scheduler.activate(
        channel=normalized_channel,
        days=days,
        delivery_time=delivery_time,
        timezone=timezone,
        first_issue_date=expected_date,
        next_run=expected_next_run,
    )
    if not schedule.active:
        raise SetupIncompleteError("Recurring delivery was not verified as active")

    try:
        delivery_result = delivery.send(issue)
    except Exception as exc:  # adapter failures must not become a false success
        raise SetupIncompleteError("The immediate first issue could not be sent") from exc
    if not delivery_result.delivered or delivery_result.channel != normalized_channel:
        raise SetupIncompleteError("The immediate first issue was not verified as sent")

    next_run = schedule.next_run
    next_run_text = next_run.strftime("%A, %Y-%m-%d at %H:%M")
    message = (
        "Kind of News is ready. %s Your first issue was sent, and recurring "
        "delivery is active every %s at %s in %s. Next scheduled delivery: "
        "%s (%s)."
        % (
            _destination_line(normalized_channel, issue.issue_id),
            _join_days(days),
            delivery_time,
            timezone,
            next_run_text,
            timezone,
        )
    )
    return SetupResult(
        issue=issue,
        rendered_issue=rendered_issue,
        schedule=schedule,
        delivery=delivery_result,
        message=message,
    )
