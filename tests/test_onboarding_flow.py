import contextlib
import io
import json
import tempfile
import unittest
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from runner.app import run
from runner.delivery.base import DeliveryResult
from runner.models import NewsIssue
from runner.onboarding import (
    ScheduleActivation,
    SetupIncompleteError,
    SetupNotConfirmedError,
    complete_confirmed_setup,
)


FIXTURE = Path(__file__).parent / "fixtures" / "valid_issue.json"
DAYS = ("monday", "wednesday", "friday")
TIMEZONE = "America/Vancouver"


class FakeRecurringScheduler:
    def __init__(self, events=None, active=True):
        self.calls = []
        self.events = events if events is not None else []
        self.active = active

    def activate(self, **kwargs):
        self.events.append("schedule")
        self.calls.append(kwargs)
        return ScheduleActivation(active=self.active, next_run=kwargs["next_run"])


class FakeGmail:
    def __init__(self, events=None, delivered=True):
        self.issues = []
        self.events = events if events is not None else []
        self.delivered = delivered

    def send(self, issue):
        self.events.append("send")
        self.issues.append(issue)
        return DeliveryResult(channel="gmail", delivered=self.delivered, detail="fake Gmail")


class OnboardingFlowTests(unittest.TestCase):
    def setUp(self):
        raw = json.loads(FIXTURE.read_text(encoding="utf-8"))
        raw["issue_id"] = "2026-08-04"  # Tuesday: not a scheduled day.
        self.issue = NewsIssue.from_mapping(raw)

    def test_confirmed_gmail_flow_sends_issue_one_and_reports_next_run(self):
        events = []
        scheduler = FakeRecurringScheduler(events)
        gmail = FakeGmail(events)

        result = complete_confirmed_setup(
            channel="gmail",
            days=DAYS,
            timezone=TIMEZONE,
            delivery_time="06:00",
            publication_date=date(2026, 8, 4),
            issue=self.issue,
            confirmed=True,
            scheduler=scheduler,
            delivery=gmail,
        )

        self.assertEqual(len(scheduler.calls), 1)
        self.assertEqual(scheduler.calls[0]["channel"], "gmail")
        self.assertEqual(scheduler.calls[0]["days"], DAYS)
        self.assertEqual(scheduler.calls[0]["delivery_time"], "06:00")
        self.assertEqual(scheduler.calls[0]["timezone"], TIMEZONE)
        self.assertEqual(scheduler.calls[0]["first_issue_date"], "2026-08-04")
        self.assertEqual(
            scheduler.calls[0]["next_run"],
            datetime(2026, 8, 5, 6, 0, tzinfo=ZoneInfo(TIMEZONE)),
        )
        self.assertEqual(gmail.issues, [self.issue])
        self.assertEqual(events, ["schedule", "send"])
        self.assertIn("☀️ Good thing", result.rendered_issue)
        self.assertIn("📅 On this day", result.rendered_issue)
        self.assertIn("🧠 Tiny fact", result.rendered_issue)
        self.assertIn("🌱 Thought for the day", result.rendered_issue)
        self.assertIn("Check your email for Kind of News #2026-08-04.", result.message)
        self.assertIn(
            "recurring delivery is active every Monday, Wednesday, and Friday at 06:00 in America/Vancouver",
            result.message,
        )
        self.assertIn(
            "Next scheduled delivery: Wednesday, 2026-08-05 at 06:00 (America/Vancouver).",
            result.message,
        )

    def test_unconfirmed_flow_calls_neither_adapter(self):
        events = []
        scheduler = FakeRecurringScheduler(events)
        gmail = FakeGmail(events)

        with self.assertRaises(SetupNotConfirmedError):
            complete_confirmed_setup(
                channel="gmail",
                days=DAYS,
                timezone=TIMEZONE,
                delivery_time="06:00",
                publication_date=date(2026, 8, 4),
                issue=self.issue,
                confirmed=False,
                scheduler=scheduler,
                delivery=gmail,
            )

        self.assertEqual(scheduler.calls, [])
        self.assertEqual(gmail.issues, [])
        self.assertEqual(events, [])

    def test_unverified_immediate_send_is_not_reported_as_success(self):
        events = []
        scheduler = FakeRecurringScheduler(events)
        gmail = FakeGmail(events, delivered=False)

        with self.assertRaises(SetupIncompleteError):
            complete_confirmed_setup(
                channel="gmail",
                days=DAYS,
                timezone=TIMEZONE,
                delivery_time="06:00",
                publication_date=date(2026, 8, 4),
                issue=self.issue,
                confirmed=True,
                scheduler=scheduler,
                delivery=gmail,
            )

        self.assertEqual(events, ["schedule", "send"])

    def test_advanced_repo_runner_dry_run_still_writes_no_state(self):
        with tempfile.TemporaryDirectory() as directory:
            config_path = Path(directory) / "config.yml"
            config_path.write_text(
                "timezone: America/Vancouver\n"
                "schedule:\n  days: [monday, wednesday, friday]\n  time: '06:00'\n"
                "delivery:\n  channels: [gmail]\n",
                encoding="utf-8",
            )
            state_dir = Path(directory) / "state"
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                exit_code = run(
                    config_path=str(config_path),
                    requested_date="2026-08-03",
                    state_dir=str(state_dir),
                    dry_run=True,
                    fixture_path=str(FIXTURE),
                    environ={},
                )

            self.assertEqual(exit_code, 0)
            self.assertIn("Sources:", output.getvalue())
            self.assertFalse(state_dir.exists())


if __name__ == "__main__":
    unittest.main()
