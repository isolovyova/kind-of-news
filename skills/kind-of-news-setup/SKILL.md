---
name: kind-of-news-setup
description: >
  Start the Kind of News onboarding tutorial. Use when a user provides the
  public Kind of News GitHub link, asks to install or configure Kind of News,
  wants a recurring digest, or has just installed the Kind of News plugin.
  Explain the product, ask one setup question at a time, run a dry run, and
  create recurring delivery only after explicit confirmation.
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

Start with this concise explanation, adapted only when the user has already
answered part of it:

> Welcome to Kind of News. It is a small, warm, fact-checked English digest
> delivered three times a week, with one good-news story, one curiosity, one
> tiny fact, and one pressure-releasing thought. I’ll help you choose a channel,
> test one issue, and then make delivery automatic.

Then ask exactly one question:

> Where would you like to receive it: Gmail, Telegram, Slack, Discord, ntfy, or
> another connected channel?

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

## Dry run

Once the channel and schedule are known, summarize the configuration in plain
language and ask whether to run a test issue now. A dry run must:

- use the sibling `kind-of-news` skill;
- research current sources before drafting;
- use the current publication date as the issue ID;
- produce the universal intro and exactly four content blocks;
- include a source URL for every factual block;
- validate the structured issue before rendering channel text;
- send nothing.

If the user says “dry run only”, stop after showing the validated issue. Do not
create a recurring task and do not claim the automation is installed.

If research, source validation, date validation, or structure validation fails,
show the problem briefly, do not send, and do not create the schedule.

## Activate recurring delivery

After a successful dry run, show the issue and ask explicitly:

> The test issue is ready. Would you like me to turn on automatic delivery for
> [days] at [time] in [timezone] to [channel]?

Create the host's recurring automation only after the user confirms. The saved
automation prompt must be self-contained and must:

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

## Completion message

Only after the recurring task is visible and active, say that setup is
complete. Summarize:

- channel;
- cadence;
- local time and timezone;
- next run, when the host provides it;
- where the user can pause or edit the task.

Tell the user that the digest is LinkedIn-ready but is never posted to LinkedIn
automatically.
