# Codex / Claude Code setup without a user repository

The public GitHub repository is only the installation source. The user does
not need to create a GitHub repository, configure Actions, or maintain code.

## One copy-paste message

```text
Install the Kind of News plugin from https://github.com/isolovyova/kind-of-news and immediately start its setup tutorial in this same turn. Use the approved Kind of News welcome from the setup skill exactly, then ask me exactly one question at a time. Do not ask me to create a GitHub repository. Use Monday/Wednesday/Friday at 06:00 in my timezone as defaults, keep credentials in the host's secure connection flow, summarize my final channel and schedule choices, and ask: “Ready to start Kind of News? I’ll send your first issue now, then deliver it every [days] at [time] in [timezone] to [channel].” After I confirm, generate and validate the issue, activate recurring delivery for subsequent issues, and send issue #1 immediately even if today is not scheduled. Report success only after both the schedule and send succeed. If I explicitly ask for a preview or dry run, send and schedule nothing.
```

The assistant should read [`assistant-setup.md`](assistant-setup.md), install the
plugin or both skills, invoke `kind-of-news-setup`, explain the product, ask for
channel/cadence/timezone/time, connect the channel, and ask the single final
confirmation using the resolved configuration. After confirmation, it should
generate and validate the issue, activate the host scheduler for subsequent
issues, send issue #1 immediately, and verify both outcomes before reporting
success. If the user explicitly asks for a preview or dry run, it sends and
schedules nothing. The user should never be asked for the URL of a new GitHub
repository. The first response is the approved welcome in
`skills/kind-of-news-setup/SKILL.md`; it should not be shortened or replaced
with a generic summary.

## Codex / ChatGPT

In the Codex app, the assistant should install the Kind of News plugin and
invoke the `kind-of-news-setup` entrypoint. After the single final confirmation,
create a Codex recurring automation that invokes the `kind-of-news` editorial
skill for subsequent issues, then send issue #1 immediately. Report success
only after the automation is active and the immediate send is verified. The
schedule belongs to the user's Codex account, not to GitHub.

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

Then invoke:

```text
/kind-of-news:kind-of-news-setup
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
