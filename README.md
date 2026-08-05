# Kind of News

A small, warm, fact-checked English digest, delivered three times a week. Each
issue has one good thing, one curiosity, one tiny fact, and one thought that
releases pressure.

## Subscribe to the branded newsletter

If you are here as a reader, [subscribe to Kind of News on
Buttondown](https://buttondown.com/kindofnews). Buttondown manages the
subscriber list and delivers the branded newsletter. You do not need GitHub,
Codex, Claude Code, Gmail, GitHub Actions, or an individual schedule.

The assistant and GitHub paths below are for someone who explicitly wants a
private, personal-channel digest or is the newsletter owner maintaining the
author-controlled publishing workflow. A connected personal Gmail never sends
the branded newsletter.

## Start in Codex or Claude Code

If you explicitly want your own private digest in a connected channel, copy this
message into Codex or Claude Code:

```text
Install the Kind of News plugin from https://github.com/isolovyova/kind-of-news and immediately start its setup tutorial in this same turn. If I am here to read the branded newsletter, direct me to https://buttondown.com/kindofnews and do not create a personal channel, schedule, or Gmail delivery. Only if I explicitly ask for my own private connected-channel digest, use the approved Kind of News welcome from the setup skill exactly, then ask me exactly one question at a time. Do not ask me to create a GitHub repository. Use Monday/Wednesday/Friday at 06:00 in my timezone as defaults, keep credentials in the host's secure connection flow, summarize my final personal channel and schedule choices, and ask: “Ready to start Kind of News? I’ll send your first issue now, then deliver it every [days] at [time] in [timezone] to [channel].” After I confirm, generate and validate the issue, activate recurring delivery for subsequent personal issues, and send issue #1 immediately even if today is not scheduled. Report success only after both the schedule and send succeed. If I explicitly ask for a preview or dry run, send and schedule nothing. Never describe this personal path as sending the branded Buttondown newsletter.
```

### What happens next

1. **Readers subscribe directly.** Buttondown is the public newsletter path.
   It owns subscriber management and delivery; there is no reader-specific
   schedule to configure.
2. **Private digest users answer one small question at a time.** The assistant
   asks about a channel available in the current host, then uses its secure
   connector flow. If a connector or scheduler is unavailable, it tells you
   and offers the supported path. It never asks you to paste credentials into
   chat.
3. **The private path confirms once, then starts.** After you choose the
   channel, cadence, timezone, and time, the assistant summarizes the plan and
   asks for one final confirmation. After you confirm, it researches and
   validates the issue, activates recurring personal delivery, and sends issue
   #1 immediately, even if today is not scheduled. It reports success only
   after both actions succeed. A preview or dry run is available only when you
   ask for one, and sends nothing. Installing the plugin alone does not turn
   delivery on.

The defaults are English, Monday/Wednesday/Friday, and 06:00 in your timezone.
The exact channel and scheduler for a private digest depend on what your Codex
or Claude Code host supports. The branded newsletter schedule is one
author-controlled workflow described in the advanced setup.

## Optional: self-managed GitHub Actions

If you are the newsletter owner and want to manage the author-controlled
publishing workflow and its secure secret, use the [advanced GitHub Actions
setup](docs/github-actions-setup.md). It can generate, validate, and publish to
Buttondown automatically. This is not required to subscribe or to use the
private guided digest path.

## More detail

- [Assistant setup contract](docs/assistant-setup.md)
- [Codex and Claude Code setup details](docs/codex-cowork-setup.md)
- [Editorial format and research rules](skills/kind-of-news/SKILL.md)
- [Advanced author-controlled GitHub Actions setup](docs/github-actions-setup.md)

## License

MIT. See [LICENSE](LICENSE).
