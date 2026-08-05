---
name: kind-of-news-setup
description: >
  Start the Kind of News onboarding tutorial. Use when a user provides the
  public Kind of News GitHub link, asks to install or configure Kind of News,
  wants a recurring digest, or has just installed the Kind of News plugin.
  Explain the product, ask one setup question at a time, and start delivery
  only after one final explicit confirmation.
---

# Kind of News Setup

Run the user-facing onboarding wizard for Kind of News. This is the entrypoint
skill. The sibling `kind-of-news` skill is the editorial engine that researches
and writes each issue.

## Installation handoff

When this skill is activated by a GitHub-link or installation request, do not
stop at “installed”, “verified”, or “available next turn”. Begin the tutorial
in the same response whenever the host allows it. If an installer has just
finished, continue with the welcome message below instead of asking the user to
invoke another command manually.

If the host cannot invoke a newly installed skill in the current turn, the next
turn must begin with this tutorial. Do not claim that the automation is set up.

## First response

Use this response exactly. It contains the one required question:

```text
Welcome to Kind of News.

I made this because I got tired of opening the news and feeling worse, while still wanting to know what was going on in the world.

I wanted a small, useful dose of things that are interesting, strange, hopeful, or worth learning. So, three times a week, Kind of News brings you one good thing, one curiosity, one tiny fact, and a thought to leave you a little less clenched.

The name is a small nod to kindness. The news can be serious without being cruel to your nervous system.

Where would you like to receive it: Gmail, Telegram, Slack, Discord, ntfy, or another connected channel?
```

Do not ask about timezone, credentials, or scheduling in the first question.

## One-question setup flow

Keep the following order and ask only one question per turn:

1. **Channel.** Offer only channels available in the current host. If the user
   names an unavailable channel, explain that limitation and offer the nearest
   supported option. Never silently switch channels.
2. **Connection.** Start the host's approved OAuth or connector flow. For a
   bot or webhook, direct the user to the host's secure credential UI or secret
   store. Never request or echo a token, OAuth secret, refresh token, bot token,
   chat ID, or webhook URL in chat.
3. **Language.** Default to English. Ask only if the user wants another
   language and the host/content workflow supports it.
4. **Cadence.** Default to Monday, Wednesday, and Friday.
5. **Timezone.** Use the host's detected timezone when available; otherwise
   default to `America/Vancouver` and ask the user to confirm or change it.
6. **Time.** Default to `06:00` in the confirmed timezone.

After each answer, briefly confirm the value and ask the next unanswered
question. Do not show YAML, Python, GitHub Actions, API schemas, or secret names
in the normal onboarding conversation.

## Final confirmation, first issue, and recurring delivery

Once the user has answered the channel, cadence, timezone, and time questions,
summarize the configuration in plain language and ask exactly one final
confirmation:

> Ready to start Kind of News? I’ll send your first issue now, then deliver it
> every [days] at [time] in [timezone] to [channel].

Do not deliver or create a recurring task before the user gives an affirmative
answer. Do not surface a preview or dry-run choice by default.

After affirmative confirmation, use the sibling `kind-of-news` skill to:

- research current sources before drafting;
- use the current publication date as the issue ID;
- produce the universal intro and exactly four content blocks;
- include a source URL for every factual block directly in its numbered Sources item;
- validate the structured issue before rendering channel text.

If research, source validation, date validation, or structure validation fails,
show the problem briefly, do not activate the schedule, and do not send.

After the issue passes validation, activate the selected host's recurring
schedule for subsequent issues, then send issue #1 immediately through the
already connected channel. The immediate send happens even when today is not
one of the selected days; the schedule controls only later issues. Verify both
schedule activation and the immediate send before reporting success. If either
step fails or cannot be verified, say that setup is incomplete and do not claim
that recurring delivery is active. Where the host allows it, avoid leaving a
partially activated schedule running after a failed first send.

The saved automation prompt must be self-contained and must:

- invoke the installed `kind-of-news` editorial skill;
- research and fact-check before drafting;
- preserve the four-block format and source links;
- use the publication date as the issue ID;
- skip a channel that already succeeded for the same issue ID;
- stop all delivery when validation fails;
- send through the already authorized channel without asking for approval on
  every future run;
- never reveal or request secrets in the run conversation.

Use the native recurring automation or scheduled-task feature of the current
host. Do not substitute GitHub Actions in the default no-repository flow.

For Codex, use the Codex app's recurring automation when available. For
ChatGPT, use its Scheduled Tasks surface. For Claude Code, use a Desktop local
scheduled task or an eligible cloud Routine, and explain the machine/repository
requirements before saving it.

## Preview-only option

If the user explicitly asks for a “dry run” or “preview only”, generate and
validate the issue, show it, and send nothing. Do not create or activate a
recurring task on that path. This preview option is opt-in and is not part of
the normal first-user flow.

## Completion message

Only after the recurring task is visible and active *and* issue #1 has been
sent successfully, say that setup is complete. Do not say delivery is active if
either verification is missing or failed. Summarize:

- channel;
- confirmation that issue #1 was sent;
- cadence;
- local time and timezone;
- next run, when the host provides it;
- where the user can pause or edit the task.

Tell the user where issue #1 should appear. For Gmail, say explicitly:

> Check your email for Kind of News #YYYY-MM-DD.

Name the next scheduled delivery with its weekday, date, local time, and
timezone. Do not say that delivery is active or imply that the first issue was
sent until both the schedule and the immediate send have been verified.

Tell the user that the digest is LinkedIn-ready but is never posted to LinkedIn
automatically.
