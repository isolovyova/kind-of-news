# Buttondown Welcome Issue

This is the operator handoff for the branded reader path. The repository
prepares the evergreen body at
[`templates/buttondown-welcome-issue.md`](../templates/buttondown-welcome-issue.md);
it does not change Buttondown settings or send anything.
This is separate from the private Codex or Claude Code install path, where each
user can choose a connected personal channel.

The goal is one separate Welcome Issue for each newly confirmed subscriber.
The M/W/F broadcast is a later, owner-controlled publication path. It must not
be used as the subscriber welcome, and it must not be enabled until the owner
has completed the welcome test and the other final checks.

Buttondown currently documents its native Welcome email, Automations, and
Welcome Sequences as features on the Buttondown Standard plan. Confirm that
the newsletter's plan includes the selected feature before paying for or
changing anything.

## Choose exactly one immediate mechanism

Use one of the following. Do not enable both, or a new subscriber could receive
two Welcome Issues.

### Preferred: `subscriber.confirmed` automation

1. In Buttondown, open the **Kind of News** newsletter and confirm that the
   Automations feature is available on the current plan.
2. Open **Settings → Automations** (or the Welcome Sequence area) and create a
   new automation whose trigger is **subscriber confirmed** (`subscriber.confirmed`).
3. Add one **Send an email** action with no delay: choose an existing email
   containing the body from `templates/buttondown-welcome-issue.md`.
4. When creating that existing email, use `Welcome to Kind of News` as the
   subject, copy only the body below the template separator, keep Buttondown's
   own header/date and required unsubscribe/footer, and do not add a second
   `Kind of News #...` title.
5. Review the automation and activate only this one welcome mechanism.

This sends one Welcome Issue to the subscriber who triggered the confirmation;
it is not a broadcast and does not backfill or resend an issue to existing
confirmed subscribers.

### Alternative: native Welcome email

If the newsletter's plan exposes the native welcome setting instead, open
**Settings → Subscribing → Welcome**, paste the same static body, and enable
that native welcome email. Leave the `subscriber.confirmed` automation off.
This is an either/or choice: never enable the native Welcome email and the
automation for the same newsletter.

## Safe owner test

Use a new test email address that is not already a confirmed Kind of News
subscriber. Do not use the existing initial subscriber for this test.

1. Save the prepared Welcome Issue and select exactly one mechanism above.
2. Subscribe the new test address through the public page:
   <https://buttondown.com/kindofnews>.
3. Complete Buttondown's confirmation step from that test inbox.
4. Verify that exactly one Welcome Issue arrives immediately, with the
   Buttondown header and required unsubscribe/footer, the four blocks, and the
   three linked sources. Confirm that no other confirmed subscriber receives a
   message from this test.
5. If the result is wrong, disable the selected mechanism before trying again;
   do not turn on the other mechanism as a workaround.

The repository-side preparation does not subscribe the test address, activate
an automation, send a message, or alter the current recurring schedule.

## Later M/W/F broadcast

After the Welcome Issue has passed the safe test, the owner can separately
review and enable the author-controlled Monday/Wednesday/Friday broadcast.
That schedule is for subsequent issues only. It is not a substitute for the
immediate one-subscriber welcome and must not be described as active while the
public workflow remains paused.

## Buttondown references

- [Welcome email](https://docs.buttondown.com/transactional-emails-welcome)
- [Automations introduction](https://docs.buttondown.com/automations-introduction)
- [Automation actions](https://docs.buttondown.com/automation-actions)
- [Welcome sequences](https://docs.buttondown.com/welcome-sequence)
