# Kind of News

A small, warm, fact-checked English digest, delivered three times a week. Each
issue has one good thing, one curiosity, one tiny fact, and one thought that
releases pressure.

## Start in Codex or Claude Code

Copy this message into Codex or Claude Code:

```text
Install the Kind of News plugin from https://github.com/isolovyova/kind-of-news and immediately start its setup tutorial in this same turn. Use the approved Kind of News welcome from the setup skill exactly, then ask me exactly one question at a time. Do not ask me to create a GitHub repository. Use Monday/Wednesday/Friday at 06:00 in my timezone as defaults, keep credentials in the host's secure connection flow, summarize my final channel and schedule choices, and ask: “Ready to start Kind of News? I’ll send your first issue now, then deliver it every [days] at [time] in [timezone] to [channel].” After I confirm, generate and validate the issue, activate recurring delivery for subsequent issues, and send issue #1 immediately even if today is not scheduled. Report success only after both the schedule and send succeed. If I explicitly ask for a preview or dry run, send and schedule nothing.
```

### What happens next

1. **The tutorial starts right away.** The assistant installs the plugin, or the
   two skills if plugins are unavailable. You do not need a repository, code,
   GitHub Actions, or a Gmail account to begin.
2. **You answer one small question at a time.** The assistant asks about a
   delivery channel available in your current host, then uses its secure
   connector flow. If a connector or scheduler is unavailable, it tells you
   and offers the supported path. It never asks you to paste credentials into
   chat.
3. **You confirm once, then it starts.** After you choose the channel, cadence,
   timezone, and time, the assistant summarizes the plan and asks for one final
   confirmation. After you confirm, it researches and validates the issue,
   activates recurring delivery for subsequent issues, and sends issue #1
   immediately, even if today is not scheduled. It reports success only after
   both actions succeed. A preview or dry run is available only when you ask
   for one, and sends nothing. Installing the plugin alone does not turn
   delivery on.

The defaults are English, Monday/Wednesday/Friday, and 06:00 in your timezone.
The exact channel and scheduler depend on what your Codex or Claude Code host
supports.

## Optional: self-managed GitHub Actions

If you explicitly want to own a repository and manage its scheduled workflow
and secrets, use the [advanced GitHub Actions setup](docs/github-actions-setup.md).
This is not required for the guided first-user setup.

## More detail

- [Assistant setup contract](docs/assistant-setup.md)
- [Codex and Claude Code setup details](docs/codex-cowork-setup.md)
- [Editorial format and research rules](skills/kind-of-news/SKILL.md)
- [Advanced GitHub Actions setup](docs/github-actions-setup.md)

## License

MIT. See [LICENSE](LICENSE).
