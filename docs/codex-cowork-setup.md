# Codex / Claude Code setup without a user repository

The public GitHub repository is only the installation source. The user does
not need to create a GitHub repository, configure Actions, or maintain code.

## One copy-paste message

```text
Install the Kind of News skill from https://github.com/isolovyova/kind-of-news, then guide me through a recurring delivery every Monday, Wednesday, and Friday at 06:00 in my timezone. Ask one question at a time, let me choose the delivery channel, use the host's connected accounts or secure credential storage, never ask me to paste secrets into chat, run a dry run first, and create the schedule only after I confirm the first live send.
```

The assistant should read [`assistant-setup.md`](assistant-setup.md), install the
skill, ask for channel/timezone/time, connect the channel, run a dry run, and
create the host scheduler after confirmation. The user should never be asked
for the URL of a new GitHub repository.

## Codex / ChatGPT

In the Codex app, the assistant should install the `skills/kind-of-news` skill
and create a Codex recurring automation that invokes it. The schedule belongs
to the user's Codex account, not to GitHub.

In ChatGPT, use a ChatGPT Scheduled Task. Scheduled Tasks are a ChatGPT
feature, not the Codex app's scheduler. If the user is in Codex CLI or an IDE
extension, the assistant can install and use the skill there, but durable
account scheduling must be completed in a Codex app or supported ChatGPT
surface.

## Claude Code

When Claude Code plugin management is available, the assistant can install the
public plugin in user scope:

```text
/plugin marketplace add https://github.com/isolovyova/kind-of-news.git
/plugin install kind-of-news@kind-of-news --scope user
```

For a no-repository setup, use Claude Code Desktop's local scheduled task with
a small local working folder. The user's computer must be awake and the app
must be open. Claude Code cloud Routines can run while the computer is off,
but the current Routine flow may require a repository context; disclose that
constraint instead of asking the user to create one unexpectedly.

Do not use `/loop` as the permanent scheduler. It is session-scoped.

## Direct skill installation

For an advanced local install, Codex can use the standard GitHub skill
installer:

```bash
python3 /path/to/install-skill-from-github.py \
  --repo isolovyova/kind-of-news \
  --path skills/kind-of-news
```

This is a fallback for troubleshooting, not the public onboarding message.
