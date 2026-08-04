# Link-first Kind of News setup

This is the setup contract for Codex, Claude Code, or another assistant that
can read the public Kind of News link.

## Product boundary

The public GitHub repository is a distribution page for the skill. An end user
does not need to create, fork, clone, or maintain a GitHub repository.

The assistant installs the Kind of News plugin or its two skills in the user's
personal AI environment. The setup skill owns the tutorial; the editorial skill
owns research and rendering. The selected host owns the recurring task,
schedule, delivery authorization, and duplicate protection. GitHub Actions
remains available as an advanced, repo-backed alternative, not the default
onboarding path.

## Start condition

Treat either of these as an installation request:

- the user provides `https://github.com/isolovyova/kind-of-news`;
- the user says “install Kind of News”, “set up the news digest”, or asks for
  recurring delivery.

Do not start by explaining YAML, Python, GitHub Actions, OAuth scopes, or API
schemas. Start as a setup guide and keep infrastructure details behind the
conversation.

## Activation contract

Installation and onboarding are separate operations. A successful installer
message is not a completed setup.

When a user provides the public link or asks to install Kind of News:

1. Install the public plugin when the host supports plugins; otherwise install
   both `kind-of-news-setup` and `kind-of-news` from the `skills/` directory.
2. Invoke `kind-of-news-setup` immediately. Do not end the response with only
   “installed”, “verified”, or “available next turn”.
3. Begin with a short explanation of what Kind of News does, then ask exactly
   one channel question.

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
   timezone in one short summary.
4. Run a dry run. Research and validate a current issue, but do not send it.
5. Show the dry-run issue and ask for explicit confirmation before the first
   live delivery.
6. Create the recurring task in the host only after the dry run passes and the
   user confirms. The recurring task must invoke the installed editorial
   `kind-of-news` skill
   skill, preserve the four-block contract, and send through the authorized
   channel without asking for approval on every run.
7. Verify that the task is visible and active, and tell the user where to pause
   or edit it.

If the user asks for a channel that is not available in the current host,
explain the closest supported option. Do not silently fall back to a different
channel.

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
- return a structured four-block issue with source URLs;
- stop before delivery if any factual block or source validation fails;
- deliver the same validated issue to each selected channel;
- avoid duplicates when the same issue ID has already succeeded for a channel;
- retry only failed channels when the host supports per-channel state.

The product creates LinkedIn-ready text but never auto-posts to LinkedIn.
Publishing to LinkedIn remains the user's action.

## Completion criteria

Report “installed” only when all of these are true:

- the skill is installed or loaded in the user's personal host scope;
- the selected delivery account or connector is authorized without exposing a
  secret in chat;
- the dry run produced a date-matched, four-block, source-validated issue;
- the recurring task exists, is active, and shows the requested schedule;
- the first real send happened only after explicit confirmation.

For the GitHub Actions fallback, use the separate workflow instructions in the
root README. Do not mix that repo-backed flow into the default no-repository
conversation.
