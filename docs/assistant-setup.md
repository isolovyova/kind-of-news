# Link-first Kind of News setup

This is the setup contract for Codex, Claude Code, or another assistant that
can read the public Kind of News link.

## Product boundary

The public GitHub repository is a distribution page for the skill. An end user
does not need to create, fork, clone, or maintain a GitHub repository.

Kind of News has two deliberately separate paths:

- **Branded newsletter:** ordinary readers subscribe at
  <https://buttondown.com/kindofnews>. Buttondown owns the subscriber list and
  email delivery. Do not install a personal connector, create an individual
  schedule, or imply that the reader's Gmail sends this newsletter.
- **Private digest:** a user who explicitly asks for a personal copy can use
  the setup skill and a connected host channel. That path is personal-channel
  delivery, not the branded newsletter.

The assistant installs the Kind of News plugin or its two skills in the user's
personal AI environment only when the user asks for the private digest or is
the newsletter author. The setup skill owns the tutorial; the editorial skill
owns research and rendering. GitHub Actions remains an advanced,
author-controlled publishing path for generating and publishing the branded
newsletter, not a reader requirement or the default personal onboarding path.

## Start condition

Treat either of these as an installation request:

- the user provides `https://github.com/isolovyova/kind-of-news` and asks to
  install/configure it, use a private digest, or maintain the newsletter;
- the user explicitly asks to install Kind of News for a private digest, set up
  a personal news digest, or asks for personal recurring delivery.

If the user asks how to read or subscribe to Kind of News, direct them to
<https://buttondown.com/kindofnews>. Do not turn a subscription request into a
personal Gmail/Telegram setup or ask about an individual schedule.

Do not start by explaining YAML, Python, GitHub Actions, OAuth scopes, or API
schemas. Start as a setup guide and keep infrastructure details behind the
conversation.

## Activation contract

Installation and onboarding are separate operations. A successful installer
message is not a completed setup.

When a user requests installation/configuration for a private digest or author
workflow:

1. Install the public plugin when the host supports plugins; otherwise install
   both `kind-of-news-setup` and `kind-of-news` from the `skills/` directory.
2. Invoke `kind-of-news-setup` immediately. Do not end the response with only
   “installed”, “verified”, or “available next turn”.
3. Use the approved welcome in `kind-of-news-setup` exactly, then ask exactly
   one channel question.

The approved welcome is for the explicit private-digest path. If the user has
not asked for a private digest or author setup, use the Buttondown subscription
path above instead.

If the host cannot invoke a newly installed skill in the same turn, say that
   installation succeeded but start the setup wizard on the very next turn. Do
   not claim delivery is configured.

## Conversation flow

Ask one question at a time. Detect the current host when possible. If it is
not clear, ask whether the user is using Codex/ChatGPT or Claude Code.

Use these defaults unless the user changes them:

1. Delivery channel: Gmail, Telegram, Slack, Discord, ntfy, webhook, or more
   than one, subject to the connectors available in the host.
2. Language: English.
3. Cadence: Monday, Wednesday, and Friday.
4. Timezone: the user's current timezone, otherwise `America/Vancouver`.
5. Local delivery time: `06:00`.

Then follow this order:

1. Start the setup wizard described above. Do not ask the user to create a
   repository.
2. Ask for the delivery channel and connect it through the host's approved
   connector or credential screen. Never ask the user to paste a token, OAuth
   secret, refresh token, bot token, or webhook URL into chat.
3. Ask for timezone and delivery time. Confirm the resolved days, time, and
   timezone in one short summary, then ask exactly:

   > Ready to start Kind of News? I’ll send your first issue now, then deliver
   > it every [days] at [time] in [timezone] to [channel].

4. Before that final confirmation, do not generate for delivery, schedule, or
   send anything. After an affirmative answer, generate and validate the first
   issue with current sources and the four-block contract.
5. If validation fails, show the problem briefly, do not activate the schedule,
   and do not send.
6. After validation succeeds, activate the selected host schedule for
   subsequent issues, then send issue #1 immediately through the connected
   channel, even if today is not one of the selected days. Verify both actions.
7. Report setup success only after schedule activation and the immediate send
   both succeed. If either fails or cannot be verified, say setup is incomplete
   and do not claim that recurring delivery is active.
8. If the user explicitly asks for a preview or dry run, show the validated
   issue and send and schedule nothing. This is opt-in, not a default prompt.

After verified success, tell the user where issue #1 should appear. For Gmail,
say “Check your email for Kind of News #YYYY-MM-DD.” Name the next scheduled
delivery with its weekday, date, local time, and timezone.

If the user asks for a channel that is not available in the current host,
explain the closest supported option. Do not silently fall back to a different
channel.

Never present the private Gmail/Telegram/webhook path as the branded
newsletter. The branded newsletter has one author-controlled recurring schedule:
the author runner researches and validates the four-block issue, then calls
Buttondown with `BUTTONDOWN_API_KEY` from the secure host/Actions secret store.
Buttondown manages subscribers and sends the published email. No Buttondown
draft is prepared manually in the normal author workflow, and the secret is
never placed in `config.yml` or chat.

## Host rules

### Codex / ChatGPT

Use Codex's recurring automation when the user is in the Codex app. When the
user is in ChatGPT, use ChatGPT Scheduled Tasks on a supported ChatGPT surface.
Do not describe ChatGPT Scheduled Tasks as a Codex feature: OpenAI exposes the
Scheduled page in ChatGPT, while Codex has its own automation surface.

A Codex CLI or IDE session may install and use the skill but is not itself the
durable scheduler. Direct the user to a Codex app or ChatGPT surface that
exposes the relevant automation feature.

Prefer connected Gmail, Slack, or other available integrations. Telegram and a
generic webhook require an approved connector or a secure host secret. Keep
those values out of the conversation and out of the skill files.

### Claude Code

Install the skill in the user's personal scope, or install the public Claude
plugin when the plugin command is available. For unattended cloud delivery,
use a Claude Code Routine only when the account has the required Routine
access and repository context. For a no-GitHub-repository setup, use Claude
Code Desktop's local scheduled task with a small local working folder; the
computer must be awake and the app must be open.

Do not present `/loop` as the permanent product scheduler. It is tied to a
session and is suitable for short-lived polling only.

If a Claude Code cloud Routine insists on selecting a repository, say so
plainly and offer the local Desktop task or Codex Scheduled Task path. Never
ask the user to create a GitHub repository just to install this skill.

## Delivery and safety

Every run must:

- use the current publication date as the issue ID;
- research before drafting;
- return a structured four-block issue with each factual source URL embedded in
  its corresponding numbered Sources item;
- stop before delivery if any factual block or source validation fails;
- deliver the same validated issue to each selected channel;
- avoid duplicates when the same issue ID has already succeeded for a channel;
- retry only failed channels when the host supports per-channel state.

For the branded newsletter, the author-controlled Buttondown run must complete
the same research, four-block, and source-link validation before its publish
request. A Buttondown response that does not confirm a queued or sent email is
a failure; it must not be reported as published.

The product creates LinkedIn-ready text but never auto-posts to LinkedIn.
Publishing to LinkedIn remains the user's action.

## Completion criteria

Report “installed” only when all of these are true:

- the skill is installed or loaded in the user's personal host scope;
- the selected delivery account or connector is authorized without exposing a
  secret in chat;
- the first issue was date-matched, four-block, and source-validated;
- the recurring task exists, is active, and shows the requested schedule for
  subsequent issues;
- issue #1 was sent immediately after the single final confirmation;
- both schedule activation and the immediate send were verified before claiming
  success.

For the GitHub Actions fallback, use the separate workflow instructions in the
[`github-actions-setup.md`](github-actions-setup.md). Do not mix that repo-backed
flow into the default no-repository conversation.
